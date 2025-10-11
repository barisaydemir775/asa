from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from googletrans import Translator

class CallQualityAnalyzer:
    """
    Analyzes a call center transcript for sentiment and other metrics.
    """
    def __init__(self, transcript: str):
        """
        Initializes the analyzer with a transcript.

        Args:
            transcript (str): The full text of the call transcript.
        """
        if not transcript or not isinstance(transcript, str):
            raise ValueError("Transcript must be a non-empty string.")
        self.transcript = transcript
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.translator = Translator()
        self.agent_lines = []
        self.customer_lines = []

    def _parse_transcript(self):
        """
        Separates the transcript into agent and customer lines based on prefixes.
        Handles prefixes like "Agent:" or "Customer:" case-insensitively.
        """
        lines = self.transcript.strip().split('\n')
        for line in lines:
            line = line.strip()
            if re.match(r'^\s*agent:', line, re.IGNORECASE):
                self.agent_lines.append(line.split(':', 1)[1].strip())
            elif re.match(r'^\s*customer:', line, re.IGNORECASE):
                self.customer_lines.append(line.split(':', 1)[1].strip())

    def _analyze_sentiment(self) -> dict:
        """
        Translates customer dialogue to English and then analyzes its sentiment.

        Returns:
            dict: A dictionary containing 'pos', 'neu', 'neg', and 'compound' scores.
                  Returns a zeroed dictionary if there is no customer dialogue.
        """
        if not self.customer_lines:
            return {'pos': 0, 'neu': 0, 'neg': 0, 'compound': 0}

        customer_text = " ".join(self.customer_lines)
        try:
            # Detect language and translate to English for accurate VADER analysis
            if self.translator.detect(customer_text).lang != 'en':
                 translated_text = self.translator.translate(customer_text, dest='en').text
            else:
                translated_text = customer_text
        except Exception as e:
            # If translation fails, fall back to analyzing the original text
            print(f"Translation failed: {e}. Analyzing original text.")
            translated_text = customer_text

        sentiment = self.sentiment_analyzer.polarity_scores(translated_text)
        return sentiment

    def _calculate_metrics(self) -> dict:
        """
        Calculates talk ratios and word counts.

        Returns:
            dict: A dictionary with talk ratios and word counts for agent and customer.
        """
        agent_word_count = sum(len(line.split()) for line in self.agent_lines)
        customer_word_count = sum(len(line.split()) for line in self.customer_lines)
        total_word_count = agent_word_count + customer_word_count

        if total_word_count == 0:
            return {
                'agent_talk_ratio': 0,
                'customer_talk_ratio': 0,
                'total_word_count': 0,
                'agent_word_count': 0,
                'customer_word_count': 0,
            }

        return {
            'agent_talk_ratio': round((agent_word_count / total_word_count) * 100, 2),
            'customer_talk_ratio': round((customer_word_count / total_word_count) * 100, 2),
            'total_word_count': total_word_count,
            'agent_word_count': agent_word_count,
            'customer_word_count': customer_word_count,
        }

    def analyze(self) -> dict:
        """
        Runs the full analysis pipeline on the transcript.

        Returns:
            dict: A nested dictionary containing sentiment, metrics, and raw data counts.
        """
        self._parse_transcript()

        sentiment_results = self._analyze_sentiment()
        metrics_results = self._calculate_metrics()

        return {
            "sentiment": sentiment_results,
            "metrics": metrics_results,
            "summary": {
                "agent_lines_count": len(self.agent_lines),
                "customer_lines_count": len(self.customer_lines)
            }
        }

# Example usage for direct execution and testing
if __name__ == '__main__':
    sample_transcript = """
    Agent: Merhaba, Teknik Destek'e hoş geldiniz. Benim adım Jules. Size nasıl yardımcı olabilirim?
    Customer: Merhaba, internetim çalışmıyor. Modemi yeniden başlatmayı denedim ama hiçbir şey olmuyor. Gerçekten sinirlenmeye başladım.
    Agent: Sinirlenmenizi anlıyorum. Bu konuda size kesinlikle yardımcı olabilirim. Lütfen modeminizdeki hangi ışıkların yandığını söyler misiniz?
    Customer: Güç ışığı yeşil, ancak internet ışığı kırmızı yanıp sönüyor. Bu çok berbat bir durum.
    Agent: Tamam, yanıp sönen kırmızı ışık genellikle evinize gelen sinyalde bir sorun olduğu anlamına gelir. İzninizle kendi tarafımdan bir tanılama çalıştırayım.
    Customer: Lütfen yapın. Bunun bir an önce çözülmesi gerekiyor.
    """

    try:
        analyzer = CallQualityAnalyzer(sample_transcript)
        results = analyzer.analyze()
        import json
        print(json.dumps(results, indent=2, ensure_ascii=False))
    except ValueError as e:
        print(e)