from typing import Optional

import spacy
from transformers import (
    BartForConditionalGeneration,
    BartTokenizer,
    T5ForConditionalGeneration,
    T5Tokenizer,
)

from ada.external.topic_explainer_legacy.topic_explainer_arXiv import (
    TopicExplainer,
)

# _DEFAULT_MODEL_PATH = "Falconsai/text_summarization"
_DEFAULT_MODEL_PATH = "facebook/bart-large-cnn"


class ArXivTopicExplainer(TopicExplainer):
    def __init__(self) -> None:
        self._tokenizer = BartTokenizer.from_pretrained(_DEFAULT_MODEL_PATH)
        self._model = BartForConditionalGeneration.from_pretrained(
            _DEFAULT_MODEL_PATH
        )
        self._nlp = spacy.load("en_core_web_sm")

    def get_topic_explanation(self, topic: str) -> Optional[str]:
        documents = [self._nlp(text) for text in self.get_documents()]
        pseudo_document = ""
        take_next = False
        document_count = 0
        for doc in documents:
            for sentence in doc.sents:
                if topic.lower() in sentence.text.lower():
                    pseudo_document += sentence.text + " "
                    document_count += 1
                    take_next = True
                elif take_next:
                    pseudo_document += sentence.text + " "
                    take_next = False

        input_ids = self._tokenizer.encode(
            pseudo_document, return_tensors="pt", max_length=512
        )
        decoder_input_ids = self._tokenizer.encode(
            f"'{topic}' is ", return_tensors="pt"
        )
        summary_ids = self._model.generate(
            input_ids,
            num_beams=4,
            max_length=100,
            early_stopping=True,
            # decoder_input_ids=decoder_input_ids,
        )
        summary = self._tokenizer.decode(
            summary_ids[0], skip_special_tokens=True
        )
        print(f"Document count: {document_count}")
        return summary

    def get_documents(self):
        return [
            "Conversational search presents opportunities to support users in their search activities to improve the effectiveness and efficiency of search while reducing their cognitive load. Limitations of the potential competency of conversational agents restrict the situations for which conversational search agents can replace human intermediaries. It is thus more interesting, initially at least, to investigate opportunities for conversational interaction to support less complex information retrieval tasks, such as typical web search, which do not require human-level intelligence in the conversational agent. In order to move towards the development of a system to enable conversational search of this type, we need to understand their required capabilities. To progress our understanding of these, we report a study examining the behaviour of users when using a standard web search engine, designed to enable us to identify opportunities to support their search activities using a conversational agent. ",
            "The article proposes a system for knowledge-based conversation designed for Social Robots and other conversational agents. The proposed system relies on an Ontology for the description of all concepts that may be relevant conversation topics, as well as their mutual relationships. The article focuses on the algorithm for Dialogue Management that selects the most appropriate conversation topic depending on the user's input. Moreover, it discusses strategies to ensure a conversation flow that captures, as more coherently as possible, the user's intention to drive the conversation in specific directions while avoiding purely reactive responses to what the user says. To measure the quality of the conversation, the article reports the tests performed with 100 recruited participants, comparing five conversational agents: (i) an agent addressing dialogue flow management based only on the detection of keywords in the speech, (ii) an agent based both on the detection of keywords and the Content Classification feature of Google Cloud Natural Language, (iii) an agent that picks conversation topics randomly, (iv) a human pretending to be a chatbot, and (v) one of the most famous chatbots worldwide: Replika. The subjective perception of the participants is measured both with the SASSI (Subjective Assessment of Speech System Interfaces) tool, as well as with a custom survey for measuring the subjective perception of coherence. ",
            "Previous studies have highlighted the benefits of pedagogical conversational agents using socially-oriented conversation with students. In this work, we examine the effects of a conversational agent's use of affiliative and self-defeating humour -- considered conducive to social well-being and enhancing interpersonal relationships -- on learners' perception of the agent and attitudes towards the task. Using a between-subjects protocol, 58 participants taught a conversational agent about rock classification using a learning-by-teaching platform, the Curiosity Notebook. While all agents were curious and enthusiastic, the style of humour was manipulated such that the agent either expressed an affiliative style, a self-defeating style, or no humour. Results demonstrate that affiliative humour can significantly increase motivation and effort, while self-defeating humour, although enhancing effort, negatively impacts enjoyment. Findings further highlight the importance of understanding learner characteristics when using humour. ",
            "Databases for OLTP are often the backbone for applications such as hotel room or cinema ticket booking applications. However, developing a conversational agent (i.e., a chatbot-like interface) to allow end-users to interact with an application using natural language requires both immense amounts of training data and NLP expertise. This motivates CAT, which can be used to easily create conversational agents for transactional databases. The main idea is that, for a given OLTP database, CAT uses weak supervision to synthesize the required training data to train a state-of-the-art conversational agent, allowing users to interact with the OLTP database. Furthermore, CAT provides an out-of-the-box integration of the resulting agent with the database. As a major difference to existing conversational agents, agents synthesized by CAT are data-aware. This means that the agent decides which information should be requested from the user based on the current data distributions in the database, which typically results in markedly more efficient dialogues compared with non-data-aware agents. We publish the code for CAT as open source. ",
            " This study investigated the effect of synthetic voice of conversational agent trained with spontaneous speech on human interactants. Specifically, we hypothesized that humans will exhibit more social responses when interacting with conversational agent that has a synthetic voice built on spontaneous speech. Typically, speech synthesizers are built on a speech corpus where voice professionals read a set of written sentences. The synthesized speech is clear as if a newscaster were reading a news or a voice actor were playing an anime character. However, this is quite different from spontaneous speech we speak in everyday conversation. Recent advances in speech synthesis enabled us to build a speech synthesizer on a spontaneous speech corpus, and to obtain a near conversational synthesized speech with reasonable quality. By making use of these technology, we examined whether humans produce more social responses to a spontaneously speaking conversational agent. We conducted a large-scale conversation experiment with a conversational agent whose utterances were synthesized with the model trained either with spontaneous speech or read speech. The result showed that the subjects who interacted with the agent whose utterances were synthesized from spontaneous speech tended to show shorter response time and a larger number of backchannels. The result of a questionnaire showed that subjects who interacted with the agent whose utterances were synthesized from spontaneous speech tended to rate their conversation with the agent as closer to a human conversation. These results suggest that speech synthesis built on spontaneous speech is essential to realize a conversational agent as a social actor. ",
            "Large-scale language technologies are increasingly used in various forms of communication with humans across different contexts. One particular use case for these technologies is conversational agents, which output natural language text in response to prompts and queries. This mode of engagement raises a number of social and ethical questions. For example, what does it mean to align conversational agents with human norms or values? Which norms or values should they be aligned with? And how can this be accomplished? In this paper, we propose a number of steps that help answer these questions. We start by developing a philosophical analysis of the building blocks of linguistic communication between conversational agents and human interlocutors. We then use this analysis to identify and formulate ideal norms of conversation that can govern successful linguistic communication between humans and conversational agents. Furthermore, we explore how these norms can be used to align conversational agents with human values across a range of different discursive domains. We conclude by discussing the practical implications of our proposal for the design of conversational agents that are aligned with these norms and values. ",
            "The recent advent of large language models (LLM) has resulted in high-performing conversational agents such as chatGPT. These agents must remember key information from an ongoing conversation to provide responses that are contextually relevant to the user. However, these agents have limited memory and can be distracted by irrelevant parts of the conversation. While many strategies exist to manage conversational memory, users currently lack affordances for viewing and controlling what the agent remembers, resulting in a poor mental model and conversational breakdowns. In this paper, we present Memory Sandbox, an interactive system and design probe that allows users to manage the conversational memory of LLM-powered agents. By treating memories as data objects that can be viewed, manipulated, recorded, summarized, and shared across conversations, Memory Sandbox provides interaction affordances for users to manage how the agent should `see' the conversation. ",
            "The dialogue experience with conversational agents can be greatly enhanced with multimodal and immersive interactions in virtual reality. In this work, we present an open-source architecture with the goal of simplifying the development of conversational agents operating in virtual environments. The architecture offers the possibility of plugging in conversational agents of different domains and adding custom or cloud-based Speech-To-Text and Text-To-Speech models to make the interaction voice-based. Using this architecture, we present two conversational prototypes operating in the digital health domain developed in Unity for both non-immersive displays and VR headsets. ",
            "In this work, we report on the effectiveness of our efforts to tailor the personality and conversational style of a conversational agent based on GPT-3.5 and GPT-4 through prompts. We use three personality dimensions with two levels each to create eight conversational agents archetypes. Ten conversations were collected per chatbot, of ten exchanges each, generating 1600 exchanges across GPT-3.5 and GPT-4. Using Linguistic Inquiry and Word Count (LIWC) analysis, we compared the eight agents on language elements including clout, authenticity, and emotion. Four language cues were significantly distinguishing in GPT-3.5, while twelve were distinguishing in GPT-4. With thirteen out of a total nineteen cues in LIWC appearing as significantly distinguishing, our results suggest possible novel prompting approaches may be needed to better suit the creation and evaluation of persistent conversational agent personalities or language styles. ",
            " This paper introduces RAISE (Reasoning and Acting through Scratchpad and Examples), an advanced architecture enhancing the integration of Large Language Models (LLMs) like GPT-4 into conversational agents. RAISE, an enhancement of the ReAct framework, incorporates a dual-component memory system, mirroring human short-term and long-term memory, to maintain context and continuity in conversations. It entails a comprehensive agent construction scenario, including phases like Conversation Selection, Scene Extraction, CoT Completion, and Scene Augmentation, leading to the LLMs Training phase. This approach appears to enhance agent controllability and adaptability in complex, multi-turn dialogues. Our preliminary evaluations in a real estate sales context suggest that RAISE has some advantages over traditional agents, indicating its potential for broader applications. This work contributes to the AI field by providing a robust framework for developing more context-aware and versatile conversational agents. ",
        ]


if __name__ == "__main__":
    topic = ""
    explainer = ArXivTopicExplainer()
    while True:
        topic = input("Enter a topic: ")
        if topic == "exit":
            break
        print(explainer.get_topic_explanation(topic))
