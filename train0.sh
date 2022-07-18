CUDA_VISIBLE_DEVICES="0" pdm run python src/train.py \
--accelerator gpu \
--batch_size 8 \
--accumulate_grad_batches 6 \
--precision 16 \
--max_epochs 30 \
--gradient_clip_val 1.0 \
--variances pitch energy \
--variance_levels phone phone \
--variance_transforms none none \
--variance_early_stopping none \
--decoder_layers 6 \
--decoder_kernel_sizes 9 9 9 9 9 9 \
--wandb_name "no_snr" \
--train_target_path "../data/train-clean-360-aligned" \
--num_workers 4
