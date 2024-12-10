'''
    code by TaeHwan Jung(@graykode)
    Original Paper and repository here : https://github.com/openai/gpt-2
    GPT2 Pytorch Model : https://github.com/huggingface/pytorch-pretrained-BERT
'''
import logging
from matplotlib import pyplot as plt
import torch

logger = logging.getLogger(__name__)

def load_weight(model, state_dict):
    old_keys = []
    new_keys = []
    for key in state_dict.keys():
        new_key = None
        if key.endswith(".g"):
            new_key = key[:-2] + ".weight"
        elif key.endswith(".b"):
            new_key = key[:-2] + ".bias"
        elif key.endswith(".w"):
            new_key = key[:-2] + ".weight"
        if new_key:
            old_keys.append(key)
            new_keys.append(new_key)
    for old_key, new_key in zip(old_keys, new_keys):
        state_dict[new_key] = state_dict.pop(old_key)

    missing_keys = []
    unexpected_keys = []
    error_msgs = []
    # copy state_dict so _load_from_state_dict can modify it
    metadata = getattr(state_dict, "_metadata", None)
    state_dict = state_dict.copy()
    if metadata is not None:
        state_dict._metadata = metadata

    def load(module, prefix=""):
        local_metadata = {} if metadata is None else metadata.get(prefix[:-1], {})
        module._load_from_state_dict(
            state_dict, prefix, local_metadata, True, missing_keys, unexpected_keys, error_msgs
        )
        for name, child in module._modules.items():
            if child is not None:
                load(child, prefix + name + ".")

    start_model = model
    if hasattr(model, "transformer") and all(not s.startswith('transformer.') for s in state_dict.keys()):
        start_model = model.transformer
    load(start_model, prefix="")

    # Make sure we are still sharing the output and input embeddings after loading weights
    return model

def test_samples(prompts, model, enc, device):
    out_completions = []
    for text in prompts:
        encoded = enc.encode(text)
        context = torch.tensor(encoded, device=device, dtype=torch.long).unsqueeze(0)
        completion = model.generate(context)
        out = completion[0, :].tolist()
        out = enc.decode(out)
        out_completions.append(out)
        
    return out_completions

def save_plots(train_steps, train_losses, val_steps, val_losses, val_margins, path):
    plt.figure(figsize=(9, 6))
    
    plt.plot(train_steps, train_losses, label="Train Loss", color="blue")
    plt.plot(val_steps, val_losses, label="Validation Loss", color="orange")
    plt.legend()
    plt.xlabel("Training steps")
    plt.ylabel("DPO Loss")
    plt.title("Training and Validation Loss")
    
    plt.savefig(path + "/loss_plot.png")
    
    plt.figure(figsize=(9, 6))
    plt.plot(val_steps, val_margins, label="Validation Margin", color="green")
    plt.xlabel("Training steps")
    plt.ylabel("Reward Margin")
    
    plt.savefig(path + "/margin_plot.png")