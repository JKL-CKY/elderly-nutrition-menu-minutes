import spacy
from typing import List, Dict
import re

class SpacyNutritionService:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        
        self.nutrition_keywords = {
            "蛋白质": ["protein", "蛋白质", "蛋清", "牛奶", "鱼", "瘦肉", "鸡胸", "牛肉", "豆腐"],
            "碳水化合物": ["carbohydrate", "碳水", "米饭", "面条", "面包", "馒头", "土豆", "红薯"],
            "脂肪": ["fat", "脂肪", "油", "肥肉", "奶油", "黄油"],
            "纤维": ["fiber", "纤维", "蔬菜", "水果", "芹菜", "菠菜", "西兰花"],
            "维生素": ["vitamin", "维生素", "维生", "vitamin a", "vitamin b", "vitamin c", "vitamin d", "vitamin e"],
            "矿物质": ["mineral", "矿物质", "钙", "铁", "锌", "钾", "钠"],
            "盐": ["salt", "盐", "sodium", "钠"],
            "糖": ["sugar", "糖", "蔗糖", "葡萄糖"],
            "胆固醇": ["cholesterol", "胆固醇"]
        }
        
        self.dietary_restriction_keywords = {
            "糖尿病": ["diabetes", "糖尿病", "低糖", "无糖", "控制血糖"],
            "高血压": ["hypertension", "高血压", "低盐", "少盐", "控制血压"],
            "高血脂": ["hyperlipidemia", "高血脂", "低脂", "少油", "胆固醇"],
            "肾病": ["kidney", "肾病", "低蛋白", "低钾"],
            "痛风": ["gout", "痛风", "低嘌呤", "嘌呤"],
            "过敏": ["allergy", "过敏", "过敏原", "海鲜", "花生", "坚果", "牛奶过敏"],
            "吞咽困难": ["dysphagia", "吞咽困难", "流食", "半流食", "软食", "泥状", "糊状"],
            "咀嚼困难": ["chewing", "咀嚼困难", "软食", "切碎"]
        }
        
        self.food_texture_keywords = {
            "普食": ["普通", "正常", "regular"],
            "软食": ["软", "soft", "软饭", "软食"],
            "半流食": ["半流", "semi-liquid", "粥", "稀饭"],
            "流食": ["流食", "liquid", "流质", "汤"],
            "泥状": ["泥", "泥状", "pureed", "糊状"],
            "切碎": ["切碎", "切碎末", "minced"]
        }

    def extract_nutrition_mentions(self, text: str) -> Dict[str, List[str]]:
        doc = self.nlp(text)
        extracted = {nutrient: [] for nutrient in self.nutrition_keywords}
        
        for token in doc:
            token_text = token.text.lower()
            for nutrient, keywords in self.nutrition_keywords.items():
                for kw in keywords:
                    if kw.lower() in token_text or kw.lower() in text.lower():
                        if kw not in extracted[nutrient]:
                            extracted[nutrient].append(kw)
        
        for ent in doc.ents:
            ent_text = ent.text.lower()
            for nutrient, keywords in self.nutrition_keywords.items():
                for kw in keywords:
                    if kw.lower() in ent_text:
                        if kw not in extracted[nutrient]:
                            extracted[nutrient].append(kw)
        
        return {k: v for k, v in extracted.items() if v}

    def extract_dietary_restrictions(self, text: str) -> Dict[str, List[str]]:
        doc = self.nlp(text)
        restrictions = {cond: [] for cond in self.dietary_restriction_keywords}
        
        text_lower = text.lower()
        for condition, keywords in self.dietary_restriction_keywords.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    if kw not in restrictions[condition]:
                        restrictions[condition].append(kw)
        
        return {k: v for k, v in restrictions.items() if v}

    def extract_food_texture(self, text: str) -> List[str]:
        textures = []
        text_lower = text.lower()
        
        for texture, keywords in self.food_texture_keywords.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    if texture not in textures:
                        textures.append(texture)
        
        return textures

    def extract_nutrition_values(self, text: str) -> Dict[str, float]:
        values = {}
        
        patterns = [
            (r"(\d+(?:\.\d+)?)\s*(?:kcal|千卡|卡路里|calories?)", "calories"),
            (r"蛋白质\s*[:：]?\s*(\d+(?:\.\d+)?)\s*g", "protein"),
            (r"碳水\s*[:：]?\s*(\d+(?:\.\d+)?)\s*g", "carbohydrates"),
            (r"脂肪\s*[:：]?\s*(\d+(?:\.\d+)?)\s*g", "fat"),
            (r"钠\s*[:：]?\s*(\d+(?:\.\d+)?)\s*mg", "sodium"),
            (r"盐\s*[:：]?\s*(\d+(?:\.\d+)?)\s*g", "salt"),
            (r"纤维\s*[:：]?\s*(\d+(?:\.\d+)?)\s*g", "fiber"),
        ]
        
        for pattern, key in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                values[key] = float(match.group(1))
        
        return values

    def extract_all_requirements(self, text: str) -> Dict:
        return {
            "nutrition_mentions": self.extract_nutrition_mentions(text),
            "dietary_restrictions": self.extract_dietary_restrictions(text),
            "food_texture": self.extract_food_texture(text),
            "nutrition_values": self.extract_nutrition_values(text)
        }
