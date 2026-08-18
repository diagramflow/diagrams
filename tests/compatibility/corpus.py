from pathlib import Path
from typing import Callable

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.azure.compute import VM
from diagrams.azure.database import SQLDatabases
from diagrams.c4 import Container, Database, Person, Relationship, System, SystemBoundary
from diagrams.custom import Custom
from diagrams.gcp.compute import ComputeEngine
from diagrams.gcp.database import SQL
from diagrams.generic.device import Mobile
from diagrams.k8s.compute import Pod
from diagrams.k8s.network import Service
from diagrams.onprem.database import Postgresql
from diagrams.saas.chat import Slack

RenderFunc = Callable[[Path, str], Path]


def _diagram(name: str, filename: Path, outformat: str) -> Diagram:
    return Diagram(
        name=name,
        filename=str(filename),
        direction="LR",
        outformat=outformat,
        show=False,
        graph_attr={"dpi": "96", "pad": "0.5"},
    )


def _output_path(filename: Path, outformat: str) -> Path:
    return filename.with_suffix(f".{outformat}")


def core_cluster_edge(filename: Path, outformat: str) -> Path:
    with _diagram("Core Cluster Edge", filename, outformat):
        with Cluster("Service Tier"):
            api = EC2("api", nodeid="core_api")
            worker = EC2("worker", nodeid="core_worker")
        api >> Edge(label="enqueue", color="darkgreen") >> worker
    return _output_path(filename, outformat)


def aws_compute_database(filename: Path, outformat: str) -> Path:
    with _diagram("AWS Compute Database", filename, outformat):
        EC2("web", nodeid="aws_web") >> Edge(label="reads") >> RDS("db", nodeid="aws_db")
    return _output_path(filename, outformat)


def azure_compute_database(filename: Path, outformat: str) -> Path:
    with _diagram("Azure Compute Database", filename, outformat):
        VM("app", nodeid="azure_app") >> Edge(label="queries") >> SQLDatabases("sql", nodeid="azure_sql")
    return _output_path(filename, outformat)


def gcp_compute_database(filename: Path, outformat: str) -> Path:
    with _diagram("GCP Compute Database", filename, outformat):
        ComputeEngine("app", nodeid="gcp_app") >> Edge(label="queries") >> SQL("sql", nodeid="gcp_sql")
    return _output_path(filename, outformat)


def k8s_compute_network(filename: Path, outformat: str) -> Path:
    with _diagram("Kubernetes Compute Network", filename, outformat):
        Pod("pod", nodeid="k8s_pod") >> Edge(label="exposes") >> Service("svc", nodeid="k8s_service")
    return _output_path(filename, outformat)


def generic_devices(filename: Path, outformat: str) -> Path:
    with _diagram("Generic Devices", filename, outformat):
        Mobile("mobile", nodeid="generic_mobile") >> Edge(label="calls") >> EC2("api", nodeid="generic_api")
    return _output_path(filename, outformat)


def onprem_database(filename: Path, outformat: str) -> Path:
    with _diagram("On-Prem Database", filename, outformat):
        EC2("app", nodeid="onprem_app") >> Edge(label="writes") >> Postgresql("postgres", nodeid="onprem_postgres")
    return _output_path(filename, outformat)


def saas_chat(filename: Path, outformat: str) -> Path:
    with _diagram("SaaS Chat", filename, outformat):
        EC2("bot", nodeid="saas_bot") >> Edge(label="posts") >> Slack("channel", nodeid="saas_slack")
    return _output_path(filename, outformat)


def c4_context(filename: Path, outformat: str) -> Path:
    with _diagram("C4 Context", filename, outformat):
        user = Person("User", "Creates diagrams", nodeid="c4_user")
        system = System("DiagramFlow", "Generates architecture diagrams", nodeid="c4_system")
        with SystemBoundary("DiagramFlow"):
            api = Container("Generate API", "FastAPI", "Runs trusted diagram code", nodeid="c4_generate_api")
            store = Database("Artifacts", "Object storage", "Stores generated images", nodeid="c4_artifacts")
        user >> Relationship("requests") >> system
        system >> Relationship("renders") >> api
        api >> Relationship("stores") >> store
    return _output_path(filename, outformat)


def custom_icon(filename: Path, outformat: str) -> Path:
    icon_path = Path(__file__).resolve().parents[2] / "resources" / "generic" / "blank" / "blank.png"
    with _diagram("Custom Icon", filename, outformat):
        custom = Custom("custom", str(icon_path), nodeid="custom_icon")
        target = EC2("target", nodeid="custom_target")
        custom >> Edge(label="wraps") >> target
    return _output_path(filename, outformat)


CASES: dict[str, RenderFunc] = {
    "core_cluster_edge": core_cluster_edge,
    "aws_compute_database": aws_compute_database,
    "azure_compute_database": azure_compute_database,
    "gcp_compute_database": gcp_compute_database,
    "k8s_compute_network": k8s_compute_network,
    "generic_devices": generic_devices,
    "onprem_database": onprem_database,
    "saas_chat": saas_chat,
    "c4_context": c4_context,
    "custom_icon": custom_icon,
}
