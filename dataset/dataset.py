from torch.utils.data import Dataset
import torch
import json
import os
import numpy as np
from PIL import Image
import math
from torchvision import transforms
from configparser import ConfigParser
from utils.configurator import Configurator


configurator = Configurator()

DATASET_ROOT_PATH = configurator.get('Dataset', 'dataset_root_path')
CORRECT_DATASET_ROOT_PATH = configurator.get('Dataset', 'correct_dataset_root_path')
INCORRECT_DATASET_ROOT_PATH = configurator.get('Dataset', 'incorrect_dataset_root_path')

CORRECT_SAMPLES_NUMBER = 67048              # but 67049 officially declared
INCORRECT_SAMPLES_NUMBER = 66734

VGG_IMG_SIZE = 224


class LazyDataset(Dataset):
    def __init__(self, mode='train'):
        self._mode = mode
        self._samples_path = []
        self._correct_samples_number = self._incorrect_samples_number = 0
        self._test_correct_samples_number = self._test_incorrect_samples_number = 0

        for dir in os.listdir(CORRECT_DATASET_ROOT_PATH):
            current_path = os.path.abspath(os.path.join(CORRECT_DATASET_ROOT_PATH, dir))
            if self._mode == 'train' and self._correct_samples_number <= (math.floor(CORRECT_SAMPLES_NUMBER * 0.8)):
                for img in os.listdir(current_path):
                    img_path = os.path.join(os.path.abspath(current_path), img)
                    self._samples_path.append(img_path)
                    self._correct_samples_number += 1
            elif self._mode == 'test':
                for img in os.listdir(current_path):
                    if self._correct_samples_number > (math.floor(CORRECT_SAMPLES_NUMBER * 0.8)):
                        img_path = os.path.join(os.path.abspath(current_path), img)
                        self._samples_path.append(img_path)
                        self._test_correct_samples_number += 1
                    self._correct_samples_number += 1

        for dir in os.listdir(INCORRECT_DATASET_ROOT_PATH):
            current_path = os.path.abspath(os.path.join(INCORRECT_DATASET_ROOT_PATH, dir))
            if self._mode == 'train' and self._incorrect_samples_number <= (math.floor(INCORRECT_SAMPLES_NUMBER * 0.8)):
                for img in os.listdir(current_path):
                    img_path = os.path.join(os.path.abspath(current_path), img)
                    self._samples_path.append(img_path)
                    self._incorrect_samples_number += 1
            elif self._mode == 'test':
                for img in os.listdir(current_path):
                    if  self._incorrect_samples_number > (math.floor(INCORRECT_SAMPLES_NUMBER * 0.8)):
                        img_path = os.path.join(os.path.abspath(current_path), img)
                        self._samples_path.append(img_path)
                        self._test_incorrect_samples_number += 1
                    self._incorrect_samples_number += 1

        if self._mode == 'train':
            print('MODE: ', self._mode, '\tCORRECT: ', self._correct_samples_number, '\t', 'INCORRECT: ', self._incorrect_samples_number)
        elif self._mode == 'test':
            print('MODE: ', self._mode, '\tCORRECT: ', self._test_correct_samples_number, '\t', 'INCORRECT: ', self._test_incorrect_samples_number)

    def __len__(self):
        return len(self._samples_path)

    def __path2image__(self, path):
        img = Image.open(path)
        return img

    def __resize__(self, img, height, width):
        return img.resize((height, width), Image.ANTIALIAS)

    def __getitem__(self, index):
        img = self.__path2image__(self._samples_path[index])
        img = self.__resize__(img, VGG_IMG_SIZE, VGG_IMG_SIZE)
        img = transforms.ToTensor()(np.array(img))
        # print(img.shape)
        if self._mode == 'train':
            label = 1 if index < self._correct_samples_number else 0        
        elif self._mode == 'test':
            label = 1 if index < self._test_correct_samples_number else 0        
        return img, label
