"""Generate every lecture figure into ../images."""

from figs_llm import build as build_llm
from figs_models import build as build_models
from figs_transformer import build as build_transformer


def main() -> None:
    build_transformer()
    build_models()
    build_llm()
    print("figures written")


if __name__ == "__main__":
    main()
