# pip install anthropic markitdown

import os
import base64
from anthropic import Anthropic
from markitdown import MarkItDown
import json

def process_documents(file_paths):
    """Process files to Markdown text with metadata"""
    md = MarkItDown()
    processed_docs = []
    
    for file_path in file_paths:
        try:
            result = md.convert(file_path)
            processed_docs.append({
                'title': os.path.basename(file_path),
                'content': result.text_content,
                'file_path': file_path
            })
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    return processed_docs

class RAGSystem:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.documents = []
        self.processor = MarkItDown()

    def add_document(self, file_path: str):
        try:
            result = self.processor.convert(file_path)
            with open(file_path, "rb") as f:
                file_data = base64.b64encode(f.read()).decode()
            
            self.documents.append({
                "title": os.path.basename(file_path),
                "content": result.text_content,
                "file_path": file_path,
                "media_type": self._get_media_type(file_path),
                "original_data": file_data
            })
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

    def _get_media_type(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        return {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }.get(ext, 'application/octet-stream')

    def ask(self, question: str, model: str = "claude-3-5-sonnet-20241022") -> str:
        if not self.documents:
            return "No documents available to answer from"

        doc_messages = []
        for doc in self.documents:
            source_type = "base64" if doc['media_type'] != 'text/plain' else "text"
            
            doc_messages.append({
                "type": "document",
                "source": {
                    "type": source_type,
                    "media_type": doc['media_type'],
                    "data": doc['original_data'] if source_type == "base64" else doc['content']
                },
                "title": doc['title'],
                "citations": {"enabled": True}
            })

        doc_messages.append({
            "type": "text",
            "text": f"Answer this question using the provided documents: {question}.You are an Q&A system that can answer questions about the documents.Just return the answer."
        })

        response = self.client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[{"role": "user", "content": doc_messages}]
        )

        return self._format_response(response)
    
    def _format_response_in_json(self, response) -> str:
        if not response.content:
            return "No answer generated"

        raw_response = {"content": []}
        
        for content in response.content:
            if content.type == "text":
                block = {
                    "type": "text",
                    "text": content.text
                }
                
                if hasattr(content, 'citations') and content.citations:
                    block["citations"] = []
                    for citation in content.citations:
                        citation_dict = {
                            "type": citation.type if hasattr(citation, 'type') else 'char_location',
                            "cited_text": citation.cited_text if hasattr(citation, 'cited_text') else '',
                            "document_title": self.documents[citation.document_index]['title'] if hasattr(citation, 'document_index') else ''
                        }
                        
                        if hasattr(citation, 'start_page_number'):
                            citation_dict.update({
                                "start_page_number": citation.start_page_number,
                                "end_page_number": getattr(citation, 'end_page_number', citation.start_page_number)
                            })
                        elif hasattr(citation, 'start_char_index'):
                            citation_dict.update({
                                "start_char_index": citation.start_char_index,
                                "end_char_index": getattr(citation, 'end_char_index', citation.start_char_index)
                            })
                            
                        block["citations"].append(citation_dict)
                raw_response["content"].append(block)
        return json.dumps(raw_response, indent=2)
    
    def _format_response(self, response) -> str:
        if not response.content:
            return "No answer generated"

        output = []
        
        for content in response.content:
            if content.type == "text":
                output.append("\nResponse Text:")
                output.append("-" * 50)
                output.append(content.text)
                
                if hasattr(content, 'citations') and content.citations:
                    output.append("\nCitations:")
                    output.append("-" * 50)
                    
                    for citation in content.citations:
                        output.append(f"\nCited Text: \"{citation.cited_text}\"")
                        output.append(f"Document: {self.documents[citation.document_index]['title']}")
                        
                        if hasattr(citation, 'start_page_number'):
                            output.append(f"Location: Page {citation.start_page_number}")
                        elif hasattr(citation, 'start_char_index'):
                            output.append(f"Location: Character {citation.start_char_index}")
                        
                        output.append("-" * 30)
        
        return "\n".join(output)


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    rag = RAGSystem(api_key=os.getenv('ANTHROPIC_API_KEY'))
    rag.add_document("documents/rag_info.txt")
    rag.add_document("documents/rag_paper.pdf")
        
    question = "what are the conclusions of the paper?"
    answer = rag.ask(question)
    
    print("Question:", question)
    print("\nAnswer:\n", answer)