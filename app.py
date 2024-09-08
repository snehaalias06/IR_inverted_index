import streamlit as st
import re
from collections import defaultdict
import os

# Helper functions
def tokenize(text):
    """Tokenize the input text into a set of lowercase words."""
    return set(re.findall(r'\b\w+\b', text.lower()))

def build_inverted_index(docs):
    """
    Build an inverted index from a collection of documents.

    Args:
        docs (dict): A dictionary where keys are document IDs and values are the document texts.

    Returns:
        dict: An inverted index where keys are words and values are sets of document IDs containing the word.
    """
    index = defaultdict(set)
    for doc_id, text in docs.items():
        words = tokenize(text)
        for word in words:
            index[word].add(doc_id)
    return index

def boolean_retrieval(index, query):
    """
    Perform Boolean retrieval based on the inverted index.

    Args:
        index (dict): The inverted index.
        query (str): The Boolean query (supports AND, OR, and NOT operations).

    Returns:
        set: A set of document IDs that match the query.
    """
    query = query.lower()
    tokens = re.findall(r'\b\w+\b', query)
    
    # Initialize result_docs as a set of all document IDs
    result_docs = set(index.keys())
    
    # Process AND operations
    if 'and' in tokens:
        terms = query.split(' and ')
        result_docs = set(index.get(terms[0].strip(), set()))
        for term in terms[1:]:
            term = term.strip()
            result_docs = result_docs.intersection(index.get(term, set()))
    
    # Process OR operations
    elif 'or' in tokens:
        terms = query.split(' or ')
        result_docs = set()
        for term in terms:
            term = term.strip()
            result_docs = result_docs.union(index.get(term, set()))
    
    # Process NOT operations
    elif 'not' in tokens:
        terms = query.split(' not ')
        if len(terms) == 2:
            term_to_exclude = terms[1].strip()
            result_docs = result_docs.difference(index.get(term_to_exclude, set()))
    
    # Handle queries without Boolean operators
    else:
        result_docs = set()
        for token in tokens:
            result_docs = result_docs.union(index.get(token, set()))
    
    return result_docs

# Streamlit app
st.title('Text Document Retrieval System')

# File uploader
uploaded_files = st.file_uploader("Upload text files", accept_multiple_files=True, type=['txt'])

if uploaded_files:
    documents = {}
    for i, uploaded_file in enumerate(uploaded_files):
        # Read the contents of the file
        text = uploaded_file.read().decode("utf-8")
        documents[f"doc{i+1}"] = text

    # Build the inverted index
    inverted_index = build_inverted_index(documents)
    
    # User query input
    query = st.text_input("Enter your query (supports AND, OR, and NOT):")
    
    if query:
        results = boolean_retrieval(inverted_index, query)
        st.write(f"Results for query: '{query}'")
        if results:
            for doc_id in results:
                st.write(f"**{doc_id}:** {documents[doc_id]}")
        else:
            st.write("No documents found matching the query.")
