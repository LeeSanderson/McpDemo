from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# Write a tool to read a doc
@mcp.tool(name="read_doc_content", description="Read the contents of a document.")
def read_doc(
    doc_id: str = Field(description="The ID of the document to read")
) -> str:    
    if doc_id not in docs:
        raise ValueError(f"Document with id {doc_id} not found.")
    return docs[doc_id]

# Write a tool to edit a doc
@mcp.tool(name="edit_document", description="Edit a document by replacing a string in the document content with a new string.")
def edit_document(
    doc_id: str = Field(description="The ID of the document to edit"), 
    old_string: str = Field(description="The text to replace, must match exactly including whitespace and punctuation"), 
    new_string: str = Field(description="The new text to insert in place of the old text")
):
    if doc_id not in docs:
        raise ValueError(f"Document with id {doc_id} not found.")
    if old_string not in docs[doc_id]:
        raise ValueError(f"String '{old_string}' not found in document with id {doc_id}.")
    docs[doc_id] = docs[doc_id].replace(old_string, new_string)
 
# Write a resource to return all doc id's
@mcp.resource(
        uri="docs://documents", 
        mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())

#  Write a resource to return the contents of a particular doc
@mcp.resource(
        uri="docs://documents/{doc_id}", 
        mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    return read_doc(doc_id)  # Reuse the read_doc tool to check if the doc exists and raise an error if it doesn't

# Write a prompt to rewrite a doc in markdown format
@mcp.prompt(
    name="format",
    description="Rewrite the content of the document in Markdown format."
)
def format_doc(doc_id: str = Field(description="The ID of the document to format")
) -> list[base.Message]: 
    prompt = f"""
    Your goal is to reformat the document to be written in markdown format. 
    
    The id of document content is as follows:
    <document>
    {doc_id}
    </document>

    Add in headers, bullet points, tables, etc as necessary.
    Use the `edit_document` tool to make edits to the document content as you reformat it.
    """

    return [base.UserMessage(content=prompt)]


# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
