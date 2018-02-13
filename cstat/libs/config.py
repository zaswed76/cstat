import yaml


def get_cfg(path):
    with open(path, "r") as obj:
        return yaml.load(obj)

def save_cfg(path, data):
    with open(path, 'w') as outfile:
        yaml.dump(data, outfile, indent=4, width=0, default_flow_style=False)

if __name__ == '__main__':
    import os
    from cstat import pth
    cfg_path = os.path.join(pth.CONFIG_DIR, "clubs.yaml")
    clubs = get_cfg(cfg_path)
    for cl in clubs.values():
        print("name - {}; id - {} max - {}".format(cl["name"], cl["id"], cl["max"]))

    clubs["les"]["max"] = 35

    save_cfg(cfg_path, clubs)