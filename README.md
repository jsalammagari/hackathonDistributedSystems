# hackathonDistributedSystems
**About the project**

**Project Overview:**
The Macroeconomics Chat Application is an innovative platform designed to provide instant, accurate responses to inquiries related to macroeconomics. This application uniquely blends advanced AI capabilities with a comprehensive database of macroeconomic literature to deliver a user-friendly and informative experience.

**Key Features:**

Intelligent Response System: At its core, the application leverages a sophisticated chatbot capable of understanding and responding to various macroeconomic queries. This includes topics like fiscal policies, economic theories, market trends, and more.

PDF Data Integration: One of the standout features of the app is its ability to fetch relevant information directly from a pre-existing collection of PDF documents. These documents encompass a wide range of macroeconomic topics, ensuring that the information provided is not only accurate but also up-to-date with current academic and professional discourse.

GPT-OpenAI Integration: In instances where the query's answer is not available in the PDF database, the application seamlessly switches to fetching responses from GPT (Generative Pre-trained Transformer), powered by OpenAI. This integration guarantees comprehensive coverage of topics, ensuring that users receive informative responses regardless of the query's complexity.

User-Friendly Interface: The application boasts a highly intuitive and visually appealing chat interface, making it accessible to users with varying levels of expertise in economics. This includes a clear, conversational display of queries and responses, and an easy-to-navigate layout.

Advanced Query Processing: The chatbot is designed to handle a spectrum of inquiries, ranging from simple definitions to complex theoretical explanations, offering users a one-stop solution for their macroeconomic queries.

Real-Time Data Retrieval: Responses are generated in real time, combining speed with accuracy, and providing an efficient educational tool for students, professionals, and anyone interested in the field of macroeconomics.

**Technical Details:**

The application is built using Flask, a lightweight and powerful web framework for Python, ensuring a robust and scalable backend.

The UI/UX is crafted using HTML, CSS (with Bootstrap), and JavaScript, offering a responsive and engaging user interface.

Integration with SQLite databases for storing user queries and responses enhances the app's performance by reducing redundant API calls and ensuring quicker access to frequently asked questions.

Specialized algorithms are implemented to search through PDF content, ensuring precise data extraction and response generation.

The app uses the latest version of the GPT model from OpenAI, providing state-of-the-art AI capabilities for query processing and response generation.

**Conclusion:**

The Macroeconomics Chat Application stands out as a cutting-edge tool for educational and professional environments. By seamlessly combining AI technology with a rich database of macroeconomic resources, it offers users a unique and interactive way to explore and understand complex economic concepts, making it a valuable asset in the field of economics education and research.


# Architecture
![macroEconomicsDistArchitecture](https://github.com/jsalammagari/hackathonDistributedSystems/assets/143347797/b6e78d31-c342-411b-bd2a-9b02c0fce9ab)

# Installation Steps
Follow these steps to set up your environment:

**Clone the Repository:**
```
git clone https://github.com/jsalammagari/hackathonDistributedSystems.git
```
**Navigate to the project directory:**
```
cd hackathonDistributedSystems
```
**Install Dependencies:**
```
pip install scikit-learn
pip install tensorflow
pip install tensorflow-hub
pip install pymupdf
pip install fitz
pip install openai
```

**Run the code:**
```
flask run -p 6001
```

![macroEconomicsChatApp](https://github.com/jsalammagari/hackathonDistributedSystems/assets/143347797/25d828dd-a38c-4fe4-8dd8-a1543efa5f3e)

The demo of the entire application can be accessed [here](https://drive.google.com/file/d/1_DvwratYo_si82v0Xj1gkR3taL-w-LSx/view?usp=drive_link).

The prompts and the prompt responses can be accessed [here](https://drive.google.com/file/d/1j1fYv_dZLzcBKBpVVuc3uPmOM_HINITs/view?usp=sharing).

