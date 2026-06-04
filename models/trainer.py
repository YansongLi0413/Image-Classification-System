"""
模型训练器 - 统一的训练循环和评估
"""
import os
import json
import time
import logging
from pathlib import Path
from collections import defaultdict

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

logger = logging.getLogger(__name__)


class Trainer:
    """
    统一训练器 - 支持所有模型
    """

    def __init__(self, model, device, save_dir, model_name, dataset_name):
        self.model = model
        self.device = device
        self.save_dir = Path(save_dir)
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.save_dir.mkdir(parents=True, exist_ok=True)

        # 训练历史
        self.history = defaultdict(list)
        self.best_acc = 0.0
        self.best_epoch = 0

    def train_epoch(self, dataloader, criterion, optimizer, epoch):
        """训练一个 epoch"""
        self.model.train()
        running_loss = 0.0
        all_preds = []
        all_labels = []

        pbar = tqdm(dataloader, desc=f'Epoch {epoch} [Train]')
        for inputs, labels in pbar:
            inputs = inputs.to(self.device)
            labels = labels.to(self.device)

            optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

            pbar.set_postfix({'loss': f'{loss.item():.4f}'})

        epoch_loss = running_loss / len(dataloader.dataset)
        epoch_acc = accuracy_score(all_labels, all_preds)

        return epoch_loss, epoch_acc

    @torch.no_grad()
    def evaluate(self, dataloader, criterion, desc='Eval'):
        """评估模型"""
        self.model.eval()
        running_loss = 0.0
        all_preds = []
        all_labels = []
        all_probs = []

        for inputs, labels in tqdm(dataloader, desc=desc):
            inputs = inputs.to(self.device)
            labels = labels.to(self.device)

            outputs = self.model(inputs)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * inputs.size(0)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

        epoch_loss = running_loss / len(dataloader.dataset)
        epoch_acc = accuracy_score(all_labels, all_preds)
        epoch_precision = precision_score(all_labels, all_preds, average='macro', zero_division=0)
        epoch_recall = recall_score(all_labels, all_preds, average='macro', zero_division=0)
        epoch_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)

        return {
            'loss': epoch_loss,
            'accuracy': epoch_acc,
            'precision': epoch_precision,
            'recall': epoch_recall,
            'f1_score': epoch_f1,
            'predictions': all_preds,
            'labels': all_labels,
        }

    def train(self, train_loader, val_loader, epochs=50, lr=0.001,
              weight_decay=1e-4, scheduler_patience=5, early_stop_patience=10):
        """完整训练流程"""
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.AdamW(
            self.model.parameters(), lr=lr, weight_decay=weight_decay
        )
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='max', factor=0.5, patience=scheduler_patience, verbose=True
        )

        no_improve = 0
        logger.info(f"开始训练 {self.model_name} on {self.dataset_name}")
        logger.info(f"设备: {self.device}, Epochs: {epochs}, LR: {lr}")

        for epoch in range(1, epochs + 1):
            # 训练
            train_loss, train_acc = self.train_epoch(
                train_loader, criterion, optimizer, epoch
            )

            # 验证
            val_results = self.evaluate(val_loader, criterion, desc=f'Epoch {epoch} [Val]')
            val_loss = val_results['loss']
            val_acc = val_results['accuracy']

            # 学习率调整
            scheduler.step(val_acc)
            current_lr = optimizer.param_groups[0]['lr']

            # 记录历史
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            self.history['lr'].append(current_lr)

            logger.info(
                f'Epoch {epoch}/{epochs} | '
                f'Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | '
                f'Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f} | '
                f'LR: {current_lr:.6f}'
            )

            # 保存最佳模型
            if val_acc > self.best_acc:
                self.best_acc = val_acc
                self.best_epoch = epoch
                no_improve = 0
                self.save_checkpoint(epoch, val_acc, is_best=True)
                logger.info(f'  ✓ 新的最佳模型! Acc: {val_acc:.4f}')
            else:
                no_improve += 1

            # 早停
            if no_improve >= early_stop_patience:
                logger.info(f'早停: {early_stop_patience} 个 epoch 无改善')
                break

        logger.info(f'训练完成! 最佳 Acc: {self.best_acc:.4f} (Epoch {self.best_epoch})')
        return self.history

    def save_checkpoint(self, epoch, acc, is_best=False):
        """保存模型检查点"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'accuracy': acc,
            'model_name': self.model_name,
            'dataset_name': self.dataset_name,
        }

        # 保存最新检查点
        ckpt_path = self.save_dir / f'{self.model_name}_{self.dataset_name}_latest.pth'
        torch.save(checkpoint, ckpt_path)

        # 保存最佳模型
        if is_best:
            best_path = self.save_dir / f'{self.model_name}_{self.dataset_name}_best.pth'
            torch.save(checkpoint, best_path)

    def load_checkpoint(self, checkpoint_path):
        """加载模型检查点"""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        logger.info(f"加载检查点: {checkpoint_path} (Acc: {checkpoint['accuracy']:.4f})")
        return checkpoint

    def save_history(self):
        """保存训练历史"""
        history_path = self.save_dir / f'{self.model_name}_{self.dataset_name}_history.json'

        # 转换 numpy float32 为 Python float
        history_dict = {}
        for k, v in self.history.items():
            history_dict[k] = [float(x) for x in v]

        history_dict['best_acc'] = float(self.best_acc)
        history_dict['best_epoch'] = self.best_epoch

        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history_dict, f, indent=2)
        logger.info(f"训练历史已保存至: {history_path}")
