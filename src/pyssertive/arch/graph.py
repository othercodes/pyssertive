import grimp


def build_graph(package: str) -> grimp.ImportGraph:
    return grimp.build_graph(package)
