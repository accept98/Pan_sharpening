#!/usr/bin/env python
# coding=utf-8
'''
Author: wjm
Date: 2020-11-11 20:37:09
LastEditTime: 2020-11-11 21:28:05
Description: Super-Resolution-Guided Progressive Pansharpening Based on a Deep Convolutional Neural Network
patch_size = 64, batch_size = 64, 
'''
import os
import torch
import torch.nn as nn
import torch.optim as optim
from model.base_net import *
from torchvision.transforms import *
import torch.nn.functional as F

class Net(nn.Module):
    def __init__(self, num_channels, base_filter, args):
        super(Net, self).__init__()

        out_channels = 4
        self.res_block_x2 = ResnetBlock(4, 32, 3, 1, 1, bias=True, scale=1, activation='relu', norm=None, pad_model=None)
        
        self.head = ConvBlock(num_channels, 48, 9, 1, 4, activation='relu', norm=None, bias = True)

        self.body = ConvBlock(48, 32, 5, 1, 2, activation='relu', norm=None, bias = True)

        self.output_conv = ConvBlock(32, out_channels, 5, 1, 2, activation='relu', norm=None, bias = True)

        for m in self.modules():
            classname = m.__class__.__name__
            if classname.find('Conv2d') != -1:
        	    # torch.nn.init.kaiming_normal_(m.weight)
        	    torch.nn.init.xavier_uniform_(m.weight, gain=1)
        	    if m.bias is not None:
        		    m.bias.data.zero_()
            elif classname.find('ConvTranspose2d') != -1:
        	    # torch.nn.init.kaiming_normal_(m.weight)
        	    torch.nn.init.xavier_uniform_(m.weight, gain=1)
        	    if m.bias is not None:
        		    m.bias.data.zero_()

    def forward(self, l_ms, b_ms, x_pan):

        NDWI = ((l_ms[:, 1, :, :] - l_ms[:, 3, :, :]) / (l_ms[:, 1, :, :] + l_ms[:, 3, :, :])).unsqueeze(1)
        NDWI = F.interpolate(NDWI, scale_factor=4, mode='bicubic')
        NDVI = ((l_ms[:, 3, :, :] - l_ms[:, 2, :, :]) / (l_ms[:, 3, :, :] + l_ms[:, 2, :, :])).unsqueeze(1)
        NDVI = F.interpolate(NDVI, scale_factor=4, mode='bicubic')
        x_f = torch.cat([b_ms, x_pan, NDVI, NDWI], 1)
        x_f = self.head(x_f)
        x_f = self.body(x_f)
        x_f = self.output_conv(x_f)
        x_f = x_f + b_ms
        
        return x_f