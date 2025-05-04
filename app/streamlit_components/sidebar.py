import streamlit as st


def sidebar_guide():
    st.sidebar.markdown(
        "## How to use - Step by step\n"
        "1. Enter your [Gemini API key](https://aistudio.google.com/app/apikey)🔑 \n"  # noqa: E501
        '2. Paste a full valid URL link to scrape HTMLs and click on **"Extract HTML documents"** 📄\n'
        "3. Set your desired parameters with sliders to modify keyword generation (recommended to leave at default)🎚️\n"
        "4. Generate keywords - every keyword generation may incur costs! Check Read me for more information.🧠\n"
        "5. Select keywords (recommended to have 5-10 keywords selected)📝\n"
        '6. Click on **"Search in browser"** to search for similar websites using google🔍'
    )

    st.sidebar.markdown(
        """
        ---
        ## **Usage**
        **Always let processes to finish before interacting with other components.**
        
        Enter a full URL in format https://www.example.com.
        
        Some website might have **anti-bot measurements**, which **block bots** from visiting their webpages. Therefore the program **won't** be able to extract HTML documents from protected websites.
        
        If there's a connection error during extraction or it mentions that the **content might be blocked**, use a different URL.
        
        ---
        """
    )


def sidebar_details():
    st.sidebar.markdown(
        """
        # 📘 Read Me

        ### **About the app**
        This app uses extracted HTML documents with AI to find relevant SEO keywords about a given website. 
        Generated keywords could be helpful in SEO strategy planning or research.
        You can also use them to find relevant webpages in any search engines on the internet.

        **Model used:** Gemini 2.0 Flash with context limit of **1 million tokens**.

        **For more details, continue reading below.**

        ---

        ### 🔑 **Gemini API key**
        API key is used to obtain SEO keywords from AI.

        For free usage, use a **free Gemini API key** from:  
        [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

        ---

        ### 📄 **Extracting HTML Documents**
        Make sure to enter your Gemini API key before extracting. It is used free of cost during extraction to calculate token length of HTML documents. 

        When you click on **"Extract HTML documents"**, the app will extract internal links from the provided URL.  

        It will then attempt to extract **desired number of HTML documents** from the **most frequently mentioned** internal links, preferably selecting those with **shorter URL paths** to obtain varied informations.

        When the model token limit is exceeded, the app will reduce the number of HTML documents used for keyword generation. 

        ⚠️ **Reminder:** Extraction takes longer with higher number of HTML documents needed to extract. (up to 1 minute)

        ---

        ### 🧠 **Generating Keywords**
        After a successful HTML extraction, the option to **generate keywords** will become available.  

        You can customize your keyword generation with the following parameters:
        - **Temperature** (controls creativity)
        - **Presence penalty** (controls variety)
        - **Language** of the generated keywords
        - **Number of keywords** to generate

        The app uses the **extracted HTML documents** as context in the prompt to generate **SEO optimized keywords**.  

        > ⚠️ **Reminder:** Generating keywords consumes tokens and may incur costs, depending on what API key is used.
        > This can lead to **large token usage**, depending on the amount of HTML documents selected and their size.

        ---

        ### 🔍 **Searching for Similar Websites**
        Generated keywords will appear as **selectable pills**.

        The **first 10 keywords** will be **pre-selected** and used to query Google Search.
        You can freely **select or deselect** any keywords to refine your search.

        Click **"Search Browser"** to open a new browser tab with **Google results based on the selected keywords**.
        """
    )
