from deep_translator import GoogleTranslator
import math


#New Translate
# class TranslationService:
def chunk_text(text, max_length=5000):
        """
        Split text into smaller chunks to handle translation limits
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            if current_length + word_length + 1 <= max_length:
                current_chunk.append(word)
                current_length += word_length + 1
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

def lang_trans(text):
        """
        Improved translation function with error handling and chunking
        """
        if text is None or (isinstance(text, float) and math.isnan(text)):
            return text
        
        if not isinstance(text, str):
            return text
        
        try:
            # Initialize translator
            translator = GoogleTranslator(source='auto', target='en')
            
            # Split text into chunks if it's too long
            chunks = chunk_text(text)
            translated_chunks = []
            
            for chunk in chunks:
                try:
                    translated_chunk = translator.translate(chunk)
                    if translated_chunk:
                        translated_chunks.append(translated_chunk)
                    else:
                        translated_chunks.append(chunk)
                except Exception as e:
                    print(f"Chunk translation failed: {str(e)}")
                    translated_chunks.append(chunk)
            
            # Join the translated chunks
            return ' '.join(translated_chunks)
        
        except Exception as e:
            print(f"Translation failed: {str(e)}")
            return text

def translate_article_data(article_data):
        """
        Translate article data with improved error handling and logging
        """
        if not isinstance(article_data, dict):
            print(f"Invalid article data type: {type(article_data)}")
            return article_data
        
        translated_data = {}
        
        for key, value in article_data.items():
            try:
                if key in ['title', 'content']:
                    # print(f"Translating {key}...")
                    translated_value = lang_trans(value)
                    if translated_value:
                        translated_data[key] = translated_value
                    else:
                        print(f"Translation failed for {key}, using original text")
                        translated_data[key] = value
                else:
                    translated_data[key] = value
                    
            except Exception as e:
                print(f"Error translating {key}: {str(e)}")
                translated_data[key] = value
        
        return translated_data