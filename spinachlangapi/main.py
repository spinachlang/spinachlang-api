from typing import List
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import os
import spinachlang
from importlib.metadata import version, PackageNotFoundError

try:
    package_version = version("spinachlangapi")
except PackageNotFoundError:
    package_version = "unspecified"


def compile_code(source: str, target: str) -> str:
    spinachlang.compile_code(code=source, language=target)
    return f"Compiled {source!r} into {target!r}"


@strawberry.type
class CompilationResult:
    target: str
    output: str


@strawberry.type
class CodeCompilation:
    source: str
    results: List[CompilationResult]


@strawberry.input
class CompilationRequest:
    source: str
    targets: List[str]


@strawberry.type
class Query:
    version: str = package_version
    ping: str = "This is a spinachlang API."


@strawberry.type
class Mutation:
    @strawberry.mutation
    def compile_codes(
        self, requests: List[CompilationRequest]
    ) -> List[CodeCompilation]:
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
    version=os.getenv("VERSION") or package_version,
    description="GraphQL API for the spinachlang compiler",
)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
