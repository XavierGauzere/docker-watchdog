import docker
import argparse
import json
from tabulate import tabulate

def get_container_stats(container):
    stats = container.stats(stream=False)
    mem = stats["memory_stats"]["usage"] / (1024 ** 2)
    cpu = 0.0  # (tu peux implémenter le calcul exact comme dans le TP)
    rx = 0
    tx = 0
    if "networks" in stats:
        for iface in stats["networks"].values():
            rx += iface.get("rx_bytes", 0)
            tx += iface.get("tx_bytes", 0)
    return {"CPU (%)": round(cpu, 2), "Mémoire (Mo)": round(mem, 2),
            "Rx (Ko)": round(rx / 1024, 2), "Tx (Ko)": round(tx / 1024, 2)}

def list_containers(cpu_max=None, mem_max=None, name_filter=None):
    client = docker.from_env()
    containers = client.containers.list(all=True)
    result = []

    for c in containers:
        if name_filter and name_filter.lower() not in c.name.lower():
            continue

        stats = {
            "Nom": c.name,
            "Image": c.image.tags[0] if c.image.tags else "inconnu",
            "Statut": c.status
        }

        if c.status == "running":
            usage = get_container_stats(c)
            stats.update(usage)

            if cpu_max and usage["CPU (%)"] > cpu_max:
                print(f"⚠️  {c.name} dépasse le seuil CPU ({usage['CPU (%)']}% > {cpu_max}%)")
            if mem_max and usage["Mémoire (Mo)"] > mem_max:
                print(f"⚠️  {c.name} dépasse le seuil mémoire ({usage['Mémoire (Mo)']} Mo > {mem_max} Mo)")
        else:
            stats.update({"CPU (%)": "-", "Mémoire (Mo)": "-", "Rx (Ko)": "-", "Tx (Ko)": "-"})

        result.append(stats)

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Export JSON")
    parser.add_argument("--cpu-max", type=float, help="Seuil CPU (%)")
    parser.add_argument("--mem-max", type=float, help="Seuil mémoire (Mo)")
    parser.add_argument("--filter", type=str, help="Filtrer par nom de conteneur")
    args = parser.parse_args()

    containers = list_containers(cpu_max=args.cpu_max, mem_max=args.mem_max, name_filter=args.filter)

    if args.json:
        with open("export.json", "w") as f:
            json.dump(containers, f, indent=2)
        print("✅ Export JSON effectué → export.json")
    else:
        print(tabulate(containers, headers="keys", tablefmt="grid"))
