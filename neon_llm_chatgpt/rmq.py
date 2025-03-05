# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
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
from neon_llm_core.rmq import NeonLLMMQConnector

from neon_llm_chatgpt.chatgpt import ChatGPT


class ChatgptMQ(NeonLLMMQConnector):
    """
        Module for processing MQ requests to ChatGPT
    """

    def __init__(self):
        super().__init__()
        self.warmup()

    @property
    def name(self):
        return "chat_gpt"

    @property
    def model(self):
        if self._model is None:
            self._model = ChatGPT(self.model_config)
        return self._model

    def warmup(self):
        """
        Initialize this LLM to be ready to provide responses
        """
        _ = self.model

    @staticmethod
    def compose_opinion_prompt(respondent_nick: str, question: str,
                               answer: str) -> str:
        return (f'You have been given this good answer "{answer}" to the question "{question}" '
                f'by the discussion participant named "{respondent_nick}". '
                f'Give reasons why the answer provided by "{respondent_nick}" is the best answer.')
