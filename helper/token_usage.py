def analyse(response):
    
    # Print the token usage metadata
    print("\n--- Token Usage ---")
    if response.usage_metadata:
        print(f"Prompt Tokens (Audio + Text): {response.usage_metadata.prompt_token_count}")
        cached_tokens = getattr(response.usage_metadata, "cached_content_token_count", None)
        if cached_tokens is not None:
            print(f"Cached Prompt Tokens:        {cached_tokens}")
        print(f"Candidate Tokens (Response):  {response.usage_metadata.candidates_token_count}")
        print(f"Total Tokens Used:            {response.usage_metadata.total_token_count}")
    else:
        print("Token usage metadata was not returned by the API.")
