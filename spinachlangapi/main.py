"""Server deffinition"""
# pylint: disable=too-few-public-methods

from importlib.metadata import version, PackageNotFoundError

from typing import List
import os

import strawberry
from fastapi import FastAPI

from strawberry.fastapi import GraphQLRouter
import spinachlang

try:
    PACKAGE_VERSION = version("spinachlangapi")
except PackageNotFoundError:
    PACKAGE_VERSION = "unspecified"


def compile_code(source: str, target: str) -> str:
    """use spinach lang to compile spinach code to an other language"""
    spinachlang.compile_code(code=source, language=target)
    return f"Compiled {source!r} into {target!r}"


@strawberry.type
class CompilationResult:
    """compilation result"""

    target: str
    output: str


@strawberry.type
class CodeCompilation:
    """code compilation"""

    source: str
    results: List[CompilationResult]


@strawberry.input
class CompilationRequest:
    """compilation requests"""

    source: str
    targets: List[str]


@strawberry.type
class Query:
    """Querys"""

    version: str = PACKAGE_VERSION
    ping: str = "This is a spinachlang API."


@strawberry.type
class Mutation:
    """Mutations"""

    @strawberry.mutation
    def compile_codes(
        self, requests: List[CompilationRequest]
    ) -> List[CodeCompilation]:
        """Compile spinach code to an other language"""
        all_results: List[CodeCompilation] = []
        for req in requests:
            results = [
                CompilationResult(
                    target=target, output=compile_code(req.source, target)
                )
                for target in req.targets
            ]
            all_results.append(CodeCompilation(source=req.source, results=results))
        return all_results


schema = strawberry.Schema(query=Query, mutation=Mutation)

app = FastAPI(
    title="spinachlangapi",
    version=os.getenv("VERSION") or PACKAGE_VERSION,
    description="GraphQL API for the spinachlang compiler",
)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
