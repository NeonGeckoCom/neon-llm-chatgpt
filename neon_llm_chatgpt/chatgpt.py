# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2021 Neongecko.com Inc.
# BSD-3
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import openai
from openai.embeddings_utils import get_embeddings, distances_from_embeddings

from typing import List, Dict
from neon_llm_core.llm import NeonLLM


class ChatGPT(NeonLLM):

    mq_to_llm_role = {
        "user": "user",
        "llm": "assistant"
    }

    def __init__(self, config):
        super().__init__(config)
        self.model_name = config["model"]
        self.role = config["role"]
        self.context_depth = config["context_depth"]
        self.max_tokens = config["max_tokens"]
        self.api_key = config["key"]
        self.num_parallel_processes = config["num_parallel_processes"]
        self.warmup()

    @property
    def model(self) -> openai:
        if self._model is None:
            openai.api_key = self.api_key
            self._model = openai
        return self._model

    @property
    def _system_prompt(self) -> str:
        return self.role

    def warmup(self):
        self.model

    def get_sorted_answer_indexes(self, question: str, answers: List[str]) -> List[int]:
        """
            Creates sorted list of answer indexes with respect to order provided in :param answers based on PPL score
            Answers are sorted from best to worst
            :param question: incoming question
            :param answers: list of answers to rank
            :returns list of indexes
        """
        if not answers:
            return []
        scores = self._score(question=question, answers=answers)
        sorted_items = sorted(zip(range(len(answers)), scores), key=lambda x: x[1])
        sorted_items_indexes = [x[0] for x in sorted_items]
        return sorted_items_indexes

    def _call_model(self, prompt: List[Dict[str, str]]) -> str:
        """
            Wrapper for ChatGPT Model generation logic
            :param prompt: Input messages sequence
            :returns: Output text sequence generated by model
        """

        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=prompt,
            temperature=0,
            max_tokens=self.max_tokens,
        )
        text = response.choices[0].message['content']

        return text

    def _assemble_prompt(self, message: str, chat_history: List[List[str]]) -> List[Dict[str, str]]:
        """
            Assembles prompt engineering logic
            Setup Guidance:
            https://platform.openai.com/docs/guides/gpt/chat-completions-api

            :param message: Incoming prompt
            :param chat_history: History of preceding conversation
            :returns: assembled prompt
        """
        messages = [
            {"role": "system", "content": self._system_prompt},
        ]
        # Context N messages
        for role, content in chat_history[-self.context_depth:]:
            role_chatgpt = self.convert_role(role)
            messages.append({"role": role_chatgpt, "content": content})
        messages.append({"role": "user", "content": message})
        return messages

    def _score(self, prompt: str, targets: List[str]) -> List[float]:
        """
            Calculates logarithmic probabilities for the list of provided text sequences
            :param prompt: Input text sequence
            :param targets: Output text sequences
            :returns: List of calculated logarithmic probabilities per output text sequence
        """

        question_embeddings, answers_embeddings = self._embeddings(question=prompt, answers=targets)
        scores_list = distances_from_embeddings(question_embeddings, answers_embeddings)
        return scores_list

    def _embeddings(self, question: str, answers: List[str]) -> (List[float], List[List[float]]):
        """
            Computes embeddings for the list of provided answers
            :param question: Question for LLM to response to
            :param answers: List of provided answers
            :returns ppl values for each answer
        """
        response = self.ask(question, [])
        texts = [response] + answers
        embeddings = get_embeddings(texts, engine="text-embedding-ada-002")
        question_embeddings = embeddings[0]
        answers_embeddings = embeddings[1:]
        return question_embeddings, answers_embeddings