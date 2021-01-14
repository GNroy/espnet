from pathlib import Path
from typing import Iterable
from typing import List
from typing import Union

import sentencepiece as spm
from typeguard import check_argument_types

from espnet2.text.abs_tokenizer import AbsTokenizer


class SentencepiecesTokenizer(AbsTokenizer):
    def __init__(self, model: Union[Path, str], bpe_alpha: float = 0.0):
        assert check_argument_types()
        self.model = str(model)
        self.bpe_alpha = bpe_alpha
        # NOTE(kamo):
        # Don't build SentencePieceProcessor in __init__()
        # because it's not picklable and it may cause following error,
        # "TypeError: can't pickle SwigPyObject objects",
        # when giving it as argument of "multiprocessing.Process()".
        self.sp = None

    def __repr__(self):
        return f'{self.__class__.__name__}(model="{self.model}")'

    def _build_sentence_piece_processor(self):
        # Build SentencePieceProcessor lazily.
        if self.sp is None:
            self.sp = spm.SentencePieceProcessor()
            self.sp.load(self.model)

    def text2tokens(self, line: str) -> List[str]:
        self._build_sentence_piece_processor()
        if self.bpe_alpha == 0.0:
            return self.sp.SampleEncodeAsPieces(line, nbest_size=1, alpha=self.bpe_alpha)
        else:
            #print(f"[DEBUG]: bpe_alpha = {self.bpe_alpha}")
            return self.sp.SampleEncodeAsPieces(line, nbest_size=-1, alpha=self.bpe_alpha)
        #return self.sp.EncodeAsPieces(line)

    def tokens2text(self, tokens: Iterable[str]) -> str:
        self._build_sentence_piece_processor()
        return self.sp.DecodePieces(list(tokens))
