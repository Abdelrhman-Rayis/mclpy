"""Pluggable ontology layer.

MCL bindings attach interface components to concepts of a domain
ontology. This module makes the ontology a first-class, swappable
dependency: anything satisfying the small Ontology protocol can back
the static checks, the concept dereferencer and the builder.

The library ships the GeoIoT ontology as its default (geoiot()), but an
RDFOntology can load ANY ontology rdflib can parse (Turtle, RDF/XML,
JSON-LD, N-Triples...), and a CompositeOntology stacks several, so
compositions may bind to SOSA, SAREF, BOT, schema.org or an in-house
vocabulary just as easily.
"""
from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Iterable, Protocol, runtime_checkable

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS


@runtime_checkable
class Ontology(Protocol):
    """What MCL needs from an ontology; implement this to plug in anything."""

    def has_term(self, uri: str) -> bool: ...
    def terms(self) -> set[str]: ...
    def describe(self, uri: str) -> dict: ...


class RDFOntology:
    """An ontology backed by an rdflib graph.

    source may be a file path, a URL, or an existing rdflib Graph.
    """

    def __init__(self, source: str | Path | Graph, format: str | None = None,
                 name: str | None = None):
        if isinstance(source, Graph):
            self.graph = source
            self.name = name or "graph"
        else:
            self.graph = Graph()
            self.graph.parse(str(source), format=format)
            self.name = name or Path(str(source)).stem
        self._terms: set[str] | None = None

    def has_term(self, uri: str) -> bool:
        return uri in self.terms()

    def terms(self) -> set[str]:
        if self._terms is None:
            self._terms = {str(s) for s in self.graph.subjects(None, None)
                           if isinstance(s, URIRef)}
        return self._terms

    def describe(self, uri: str) -> dict:
        ref = URIRef(uri)
        label = self.graph.value(ref, RDFS.label)
        comment = self.graph.value(ref, RDFS.comment)
        types = [str(t).rsplit("#", 1)[-1].rsplit("/", 1)[-1]
                 for t in self.graph.objects(ref, RDF.type)]
        return {"uri": uri,
                "label": str(label) if label else None,
                "comment": str(comment) if comment else None,
                "types": types,
                "ontology": self.name}

    def __repr__(self) -> str:
        return f"RDFOntology({self.name!r}, {len(self.graph)} triples)"


class CompositeOntology:
    """Several ontologies presented as one (first match wins on describe)."""

    def __init__(self, *ontologies: Ontology):
        if not ontologies:
            raise ValueError("CompositeOntology needs at least one ontology")
        self.parts: tuple[Ontology, ...] = ontologies

    def has_term(self, uri: str) -> bool:
        return any(o.has_term(uri) for o in self.parts)

    def terms(self) -> set[str]:
        out: set[str] = set()
        for o in self.parts:
            out |= o.terms()
        return out

    def describe(self, uri: str) -> dict:
        for o in self.parts:
            if o.has_term(uri):
                return o.describe(uri)
        return {"uri": uri, "label": None, "comment": None, "types": [],
                "ontology": None}


class Namespace:
    """Tiny convenience for building concept URIs: GIOT = Namespace(...);
    GIOT.Series -> 'http://...#Series'."""

    def __init__(self, base: str):
        self._base = base

    def __getattr__(self, term: str) -> str:
        if term.startswith("_"):
            raise AttributeError(term)
        return self._base + term

    def __getitem__(self, term: str) -> str:
        return self._base + term

    def __str__(self) -> str:
        return self._base


GEOIOT = Namespace("http://www.geoiot.org/ontology#")

_default: RDFOntology | None = None


def geoiot() -> RDFOntology:
    """The bundled GeoIoT ontology, the library default (cached)."""
    global _default
    if _default is None:
        path = resources.files("mclpy").joinpath("ontologies/geoiot.ttl")
        with resources.as_file(path) as p:
            _default = RDFOntology(p, format="turtle", name="geoiot")
    return _default
