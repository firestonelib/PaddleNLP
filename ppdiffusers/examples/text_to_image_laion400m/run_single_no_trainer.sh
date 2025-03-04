# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

python -u train_txt2img_laion400m_no_trainer.py \
    --output_dir ./laion400m_pretrain_output_no_trainer \
    --train_batch_size 6 \
    --gradient_accumulation_steps 10 \
    --learning_rate 4.6875e-5 \
    --adam_weight_decay 0.02 \
    --max_train_steps 1000000000 \
    --lr_scheduler "constant" \
    --lr_warmup_steps 0 \
    --logging_steps 50 \
    --save_steps 5000 \
    --seed 23 \
    --num_workers 6 \
    --pretrained_model_name_or_path CompVis/ldm_laion400M_pretrain \
    --file_list ./data/filelist/train.filelist.list \
    --num_inference_steps 200 \
    --model_max_length 77 \
    --tokenizer_name bert-base-uncased