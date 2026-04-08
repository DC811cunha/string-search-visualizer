"""Algoritmos de busca de padrões em strings.

Projeto acadêmico de Algoritmos Avançados.
Arquitetura baseada no padrão Strategy.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List
import time


@dataclass(frozen=True)
class ComplexityInfo:
    melhor: str
    medio: str
    pior: str
    espaco: str

    def as_dict(self) -> Dict[str, str]:
        return {
            "melhor": self.melhor,
            "medio": self.medio,
            "pior": self.pior,
            "espaco": self.espaco,
        }


class SearchStrategy(ABC):
    """Interface Strategy para os algoritmos de busca."""

    @property
    @abstractmethod
    def key(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def theoretical_complexity(self) -> ComplexityInfo:
        raise NotImplementedError

    @property
    def notes(self) -> str:
        return ""

    def complexity_dict(self) -> Dict[str, str]:
        return self.theoretical_complexity.as_dict()

    def _empty_result(self, text: str, pattern: str, start_ns: int | None = None, **extra: Any) -> Dict[str, Any]:
        elapsed = 0 if start_ns is None else time.perf_counter_ns() - start_ns
        return {
            "occurrences": [],
            "comparisons": 0,
            "time_ns": elapsed,
            "text_len": len(text),
            "pattern_len": len(pattern),
            **extra,
        }

    def _match_result(
        self,
        *,
        text: str,
        pattern: str,
        occurrences: List[int],
        comparisons: int,
        start_ns: int,
        **extra: Any,
    ) -> Dict[str, Any]:
        return {
            "occurrences": occurrences,
            "comparisons": comparisons,
            "time_ns": time.perf_counter_ns() - start_ns,
            "text_len": len(text),
            "pattern_len": len(pattern),
            **extra,
        }

    @abstractmethod
    def search(self, text: str, pattern: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def search_step_by_step(self, text: str, pattern: str) -> List[Dict[str, Any]]:
        raise NotImplementedError


class NaiveSearch(SearchStrategy):
    @property
    def key(self) -> str:
        return "naive"

    @property
    def name(self) -> str:
        return "Naive (Força Bruta)"

    @property
    def theoretical_complexity(self) -> ComplexityInfo:
        return ComplexityInfo("O(n)", "O(n * m)", "O(n * m)", "O(1)")

    @property
    def notes(self) -> str:
        return "Simples e didático, mas tende a recomparar muitos caracteres." 

    def search(self, text: str, pattern: str) -> Dict[str, Any]:
        start = time.perf_counter_ns()
        n, m = len(text), len(pattern)
        if m == 0 or m > n:
            return self._empty_result(text, pattern, start)

        occurrences: List[int] = []
        comparisons = 0
        for i in range(n - m + 1):
            j = 0
            while j < m:
                comparisons += 1
                if text[i + j] != pattern[j]:
                    break
                j += 1
            if j == m:
                occurrences.append(i)

        return self._match_result(
            text=text,
            pattern=pattern,
            occurrences=occurrences,
            comparisons=comparisons,
            start_ns=start,
        )

    def search_step_by_step(self, text: str, pattern: str) -> List[Dict[str, Any]]:
        n, m = len(text), len(pattern)
        if m == 0 or m > n:
            return [{
                "description": "Nenhum passo executado: padrão vazio ou maior que o texto.",
                "comparisons": 0,
                "window_start": 0,
            }]

        steps: List[Dict[str, Any]] = []
        comparisons = 0
        for i in range(n - m + 1):
            for j in range(m):
                comparisons += 1
                matched = text[i + j] == pattern[j]
                steps.append({
                    "text_index": i + j,
                    "pattern_index": j,
                    "window_start": i,
                    "comparisons": comparisons,
                    "match": matched,
                    "description": (
                        f"Janela em {i}: comparando texto[{i+j}]='{text[i+j]}' "
                        f"com padrão[{j}]='{pattern[j]}' -> {'match' if matched else 'mismatch'}"
                    ),
                })
                if not matched:
                    break
            else:
                steps.append({
                    "text_index": i,
                    "pattern_index": -1,
                    "window_start": i,
                    "found": True,
                    "comparisons": comparisons,
                    "description": f"Padrão encontrado na posição {i}.",
                })
        return steps


class RabinKarpSearch(SearchStrategy):
    BASE = 256
    MOD = 1_000_000_007

    @property
    def key(self) -> str:
        return "rabin_karp"

    @property
    def name(self) -> str:
        return "Rabin-Karp"

    @property
    def theoretical_complexity(self) -> ComplexityInfo:
        return ComplexityInfo("O(n + m)", "O(n + m)", "O(n * m)", "O(1)")

    @property
    def notes(self) -> str:
        return "Usa hashing para filtrar janelas candidatas antes de comparar caractere por caractere."

    def _hash(self, s: str, length: int) -> int:
        h = 0
        for i in range(length):
            h = (h * self.BASE + ord(s[i])) % self.MOD
        return h

    def search(self, text: str, pattern: str) -> Dict[str, Any]:
        start = time.perf_counter_ns()
        n, m = len(text), len(pattern)
        if m == 0 or m > n:
            return self._empty_result(text, pattern, start)

        pattern_hash = self._hash(pattern, m)
        window_hash = self._hash(text, m)
        high = pow(self.BASE, m - 1, self.MOD)
        occurrences: List[int] = []
        comparisons = 0
        collisions = 0

        for i in range(n - m + 1):
            if pattern_hash == window_hash:
                matched = True
                for j in range(m):
                    comparisons += 1
                    if text[i + j] != pattern[j]:
                        matched = False
                        collisions += 1
                        break
                if matched:
                    occurrences.append(i)

            if i < n - m:
                window_hash = (
                    self.BASE * (window_hash - ord(text[i]) * high) + ord(text[i + m])
                ) % self.MOD
                if window_hash < 0:
                    window_hash += self.MOD

        return self._match_result(
            text=text,
            pattern=pattern,
            occurrences=occurrences,
            comparisons=comparisons,
            start_ns=start,
            collisions=collisions,
            hash_base=self.BASE,
            hash_mod=self.MOD,
        )

    def search_step_by_step(self, text: str, pattern: str) -> List[Dict[str, Any]]:
        n, m = len(text), len(pattern)
        if m == 0 or m > n:
            return [{
                "description": "Nenhum passo executado: padrão vazio ou maior que o texto.",
                "comparisons": 0,
                "window_start": 0,
            }]

        pattern_hash = self._hash(pattern, m)
        window_hash = self._hash(text, m)
        high = pow(self.BASE, m - 1, self.MOD)
        steps: List[Dict[str, Any]] = [{
            "window_start": 0,
            "comparisons": 0,
            "hash_pattern": pattern_hash,
            "hash_window": window_hash,
            "description": f"Hash do padrão = {pattern_hash}. Hash inicial da janela = {window_hash}.",
        }]
        comparisons = 0

        for i in range(n - m + 1):
            same_hash = pattern_hash == window_hash
            steps.append({
                "window_start": i,
                "comparisons": comparisons,
                "hash_pattern": pattern_hash,
                "hash_window": window_hash,
                "description": (
                    f"Janela [{i}:{i+m}] com hash {window_hash}. "
                    f"{'Hash igual ao padrão' if same_hash else 'Hash diferente do padrão'}"
                ),
            })
            if same_hash:
                matched = True
                for j in range(m):
                    comparisons += 1
                    char_match = text[i + j] == pattern[j]
                    steps.append({
                        "text_index": i + j,
                        "pattern_index": j,
                        "window_start": i,
                        "comparisons": comparisons,
                        "match": char_match,
                        "description": (
                            f"Verificando colisão: texto[{i+j}]='{text[i+j]}' "
                            f"vs padrão[{j}]='{pattern[j]}' -> {'match' if char_match else 'mismatch'}"
                        ),
                    })
                    if not char_match:
                        matched = False
                        break
                if matched:
                    steps.append({
                        "window_start": i,
                        "comparisons": comparisons,
                        "found": True,
                        "description": f"Padrão confirmado na posição {i}.",
                    })
            if i < n - m:
                window_hash = (
                    self.BASE * (window_hash - ord(text[i]) * high) + ord(text[i + m])
                ) % self.MOD
                if window_hash < 0:
                    window_hash += self.MOD
        return steps


class KMPSearch(SearchStrategy):
    @property
    def key(self) -> str:
        return "kmp"

    @property
    def name(self) -> str:
        return "Knuth-Morris-Pratt (KMP)"

    @property
    def theoretical_complexity(self) -> ComplexityInfo:
        return ComplexityInfo("O(n)", "O(n + m)", "O(n + m)", "O(m)")

    @property
    def notes(self) -> str:
        return "Evita recomparações com a tabela LPS (Longest Prefix Suffix)."

    def _build_lps(self, pattern: str) -> List[int]:
        m = len(pattern)
        lps = [0] * m
        length = 0
        i = 1
        while i < m:
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            elif length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
        return lps

    def search(self, text: str, pattern: str) -> Dict[str, Any]:
        start = time.perf_counter_ns()
        n, m = len(text), len(pattern)
        if m == 0 or m > n:
            return self._empty_result(text, pattern, start, lps=[])

        lps = self._build_lps(pattern)
        occurrences: List[int] = []
        comparisons = 0
        i = j = 0

        while i < n:
            comparisons += 1
            if text[i] == pattern[j]:
                i += 1
                j += 1
                if j == m:
                    occurrences.append(i - j)
                    j = lps[j - 1]
            else:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1

        return self._match_result(
            text=text,
            pattern=pattern,
            occurrences=occurrences,
            comparisons=comparisons,
            start_ns=start,
            lps=lps,
        )

    def search_step_by_step(self, text: str, pattern: str) -> List[Dict[str, Any]]:
        n, m = len(text), len(pattern)
        if m == 0 or m > n:
            return [{
                "description": "Nenhum passo executado: padrão vazio ou maior que o texto.",
                "comparisons": 0,
                "window_start": 0,
                "lps": [],
            }]

        lps = self._build_lps(pattern)
        steps: List[Dict[str, Any]] = [{
            "description": f"Tabela LPS calculada: {lps}",
            "comparisons": 0,
            "window_start": 0,
            "text_index": 0,
            "pattern_index": 0,
            "lps": lps,
        }]
        comparisons = 0
        i = j = 0

        while i < n:
            comparisons += 1
            matched = text[i] == pattern[j]
            steps.append({
                "text_index": i,
                "pattern_index": j,
                "window_start": i - j,
                "comparisons": comparisons,
                "match": matched,
                "lps": lps,
                "description": (
                    f"Comparando texto[{i}]='{text[i]}' com padrão[{j}]='{pattern[j]}' "
                    f"-> {'match' if matched else 'mismatch'}"
                ),
            })

            if matched:
                i += 1
                j += 1
                if j == m:
                    pos = i - j
                    steps.append({
                        "text_index": pos,
                        "pattern_index": -1,
                        "window_start": pos,
                        "comparisons": comparisons,
                        "found": True,
                        "lps": lps,
                        "description": (
                            f"Padrão encontrado na posição {pos}. "
                            f"Próximo j recebe LPS[{m - 1}] = {lps[m - 1]}."
                        ),
                    })
                    j = lps[j - 1]
            else:
                if j != 0:
                    steps.append({
                        "text_index": i,
                        "pattern_index": j,
                        "window_start": i - j,
                        "comparisons": comparisons,
                        "lps": lps,
                        "description": (
                            f"Mismatch com j={j}. Recuando j para LPS[{j - 1}] = {lps[j - 1]} sem voltar i."
                        ),
                    })
                    j = lps[j - 1]
                else:
                    i += 1
        return steps


class BoyerMooreSearch(SearchStrategy):
    @property
    def key(self) -> str:
        return "boyer_moore"

    @property
    def name(self) -> str:
        return "Boyer-Moore (Bad Character)"

    @property
    def theoretical_complexity(self) -> ComplexityInfo:
        return ComplexityInfo("O(n / m)", "O(n)", "O(n * m)", "O(sigma)")

    @property
    def notes(self) -> str:
        return "Implementação da heurística Bad Character, com comparações da direita para a esquerda."

    def _bad_char_table(self, pattern: str) -> Dict[str, int]:
        table: Dict[str, int] = {}
        for i, ch in enumerate(pattern):
            table[ch] = i
        return table

    def search(self, text: str, pattern: str) -> Dict[str, Any]:
        start = time.perf_counter_ns()
        n, m = len(text), len(pattern)
        if m == 0 or m > n:
            return self._empty_result(text, pattern, start, bad_char={})

        bad_char = self._bad_char_table(pattern)
        occurrences: List[int] = []
        comparisons = 0
        s = 0

        while s <= n - m:
            j = m - 1
            while j >= 0:
                comparisons += 1
                if pattern[j] != text[s + j]:
                    break
                j -= 1

            if j < 0:
                occurrences.append(s)
                s += m - bad_char.get(text[s + m], -1) if s + m < n else 1
            else:
                s += max(1, j - bad_char.get(text[s + j], -1))

        return self._match_result(
            text=text,
            pattern=pattern,
            occurrences=occurrences,
            comparisons=comparisons,
            start_ns=start,
            bad_char=bad_char,
        )

    def search_step_by_step(self, text: str, pattern: str) -> List[Dict[str, Any]]:
        n, m = len(text), len(pattern)
        if m == 0 or m > n:
            return [{
                "description": "Nenhum passo executado: padrão vazio ou maior que o texto.",
                "comparisons": 0,
                "window_start": 0,
                "bad_char": {},
            }]

        bad_char = self._bad_char_table(pattern)
        steps: List[Dict[str, Any]] = [{
            "description": f"Tabela Bad Character: {bad_char}",
            "comparisons": 0,
            "window_start": 0,
            "bad_char": bad_char,
        }]
        comparisons = 0
        s = 0

        while s <= n - m:
            j = m - 1
            while j >= 0:
                comparisons += 1
                matched = pattern[j] == text[s + j]
                steps.append({
                    "text_index": s + j,
                    "pattern_index": j,
                    "window_start": s,
                    "comparisons": comparisons,
                    "match": matched,
                    "bad_char": bad_char,
                    "description": (
                        f"Comparando da direita para a esquerda: texto[{s+j}]='{text[s+j]}' "
                        f"vs padrão[{j}]='{pattern[j]}' -> {'match' if matched else 'mismatch'}"
                    ),
                })
                if not matched:
                    break
                j -= 1

            if j < 0:
                next_shift = m - bad_char.get(text[s + m], -1) if s + m < n else 1
                steps.append({
                    "window_start": s,
                    "comparisons": comparisons,
                    "found": True,
                    "bad_char": bad_char,
                    "description": f"Padrão encontrado na posição {s}. Próximo salto = {next_shift}.",
                })
                s += next_shift
            else:
                mismatch_char = text[s + j]
                bc_index = bad_char.get(mismatch_char, -1)
                shift = max(1, j - bc_index)
                steps.append({
                    "window_start": s,
                    "comparisons": comparisons,
                    "bad_char": bad_char,
                    "description": (
                        f"Caractere problemático '{mismatch_char}' possui última ocorrência em {bc_index}. "
                        f"Aplicando salto de {shift}."
                    ),
                })
                s += shift
        return steps


STRATEGY_REGISTRY: Dict[str, SearchStrategy] = {
    strategy.key: strategy
    for strategy in [NaiveSearch(), RabinKarpSearch(), KMPSearch(), BoyerMooreSearch()]
}
