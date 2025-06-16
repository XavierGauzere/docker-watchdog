import streamlit as st
import docker

def get_stats():
    client = docker.from_env()
    containers = client.containers.list(all=True)
    data = []
    for c in containers:
        stats = {
            "Nom": c.name,
            "Image": c.image.tags[0] if c.image.tags else "inconnu",
            "Statut": c.status
        }

        if c.status == "running":
            s = c.stats(stream=False)
            cpu_delta = s["cpu_stats"]["cpu_usage"]["total_usage"] - s["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = s["cpu_stats"]["system_cpu_usage"] - s["precpu_stats"]["system_cpu_usage"]
            cpu = (cpu_delta / system_delta) * 100 if system_delta > 0 else 0
            stats["CPU (%)"] = round(cpu, 2)
            stats["Mémoire (Mo)"] = round(s["memory_stats"]["usage"] / (1024**2), 2)
        else:
            stats["CPU (%)"] = "-"
            stats["Mémoire (Mo)"] = "-"

        data.append(stats)
    return data

st.title("Dashboard Docker temps réel")

for container in get_stats():
    statut = "🟢" if container["Statut"] == "running" else "🔴"
    st.markdown(f"### {statut} {container['Nom']}")
    st.write(container)
