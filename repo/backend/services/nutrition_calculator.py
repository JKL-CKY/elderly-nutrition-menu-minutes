from typing import Dict, Optional

class NutritionCalculator:
    @staticmethod
    def calculate_bmi(weight_kg: float, height_m: float) -> float:
        if height_m <= 0:
            return 0
        return round(weight_kg / (height_m ** 2), 1)

    @staticmethod
    def get_bmi_category(bmi: float) -> str:
        if bmi < 18.5:
            return "偏瘦"
        elif 18.5 <= bmi < 24:
            return "正常"
        elif 24 <= bmi < 28:
            return "超重"
        else:
            return "肥胖"

    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
        if gender == "男":
            bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
        return round(bmr, 0)

    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        activity_factors = {
            "卧床": 1.2,
            "轻度活动": 1.375,
            "中度活动": 1.55,
            "高度活动": 1.725,
            "非常活跃": 1.9
        }
        factor = activity_factors.get(activity_level, 1.2)
        return round(bmr * factor, 0)

    @staticmethod
    def calculate_nutrient_requirements(
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: str,
        activity_level: str,
        health_conditions: list = None
    ) -> Dict:
        bmr = NutritionCalculator.calculate_bmr(weight_kg, height_cm, age, gender)
        tdee = NutritionCalculator.calculate_tdee(bmr, activity_level)
        
        protein_per_kg = 1.0
        fat_ratio = 0.25
        carb_ratio = 0.55
        sodium_limit = 2000
        fiber_min = 25
        calcium_min = 1000
        
        if health_conditions:
            if "糖尿病" in health_conditions:
                carb_ratio = 0.45
            if "高血压" in health_conditions:
                sodium_limit = 1500
            if "肾病" in health_conditions:
                protein_per_kg = 0.8
            if "高血脂" in health_conditions:
                fat_ratio = 0.2
        
        protein = round(weight_kg * protein_per_kg, 1)
        fat = round(tdee * fat_ratio / 9, 1)
        carbohydrates = round(tdee * carb_ratio / 4, 1)
        
        return {
            "bmr": bmr,
            "tdee": tdee,
            "calories": tdee,
            "protein": protein,
            "protein_unit": "g",
            "fat": fat,
            "fat_unit": "g",
            "carbohydrates": carbohydrates,
            "carbohydrates_unit": "g",
            "fiber_min": fiber_min,
            "fiber_unit": "g",
            "sodium_limit": sodium_limit,
            "sodium_unit": "mg",
            "calcium_min": calcium_min,
            "calcium_unit": "mg",
            "water_min": 1500,
            "water_unit": "ml"
        }

    @staticmethod
    def calculate_meal_nutrition(meal_items: list) -> Dict:
        nutrition_data = {
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbohydrates": 0,
            "fiber": 0,
            "sodium": 0
        }
        
        food_database = {
            "米饭": {"calories": 116, "protein": 2.6, "fat": 0.3, "carbohydrates": 25.6, "fiber": 0.3, "sodium": 2},
            "馒头": {"calories": 221, "protein": 7, "fat": 1.1, "carbohydrates": 47, "fiber": 1.3, "sodium": 165},
            "鸡蛋": {"calories": 144, "protein": 13.3, "fat": 8.8, "carbohydrates": 2.8, "fiber": 0, "sodium": 131},
            "牛奶": {"calories": 54, "protein": 3, "fat": 3.2, "carbohydrates": 3.4, "fiber": 0, "sodium": 37},
            "瘦肉": {"calories": 143, "protein": 20.3, "fat": 6.2, "carbohydrates": 1.5, "fiber": 0, "sodium": 57},
            "鱼": {"calories": 113, "protein": 18, "fat": 4.1, "carbohydrates": 0, "fiber": 0, "sodium": 46},
            "豆腐": {"calories": 81, "protein": 8.1, "fat": 3.7, "carbohydrates": 4.2, "fiber": 0.4, "sodium": 7},
            "青菜": {"calories": 15, "protein": 1.5, "fat": 0.3, "carbohydrates": 2.7, "fiber": 1.1, "sodium": 73},
            "西兰花": {"calories": 36, "protein": 4.1, "fat": 0.6, "carbohydrates": 4.3, "fiber": 1.6, "sodium": 18},
            "胡萝卜": {"calories": 37, "protein": 1, "fat": 0.2, "carbohydrates": 8.8, "fiber": 1.1, "sodium": 71},
            "苹果": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbohydrates": 14, "fiber": 2.4, "sodium": 1},
            "香蕉": {"calories": 93, "protein": 1.4, "fat": 0.2, "carbohydrates": 22, "fiber": 1.2, "sodium": 1},
            "粥": {"calories": 46, "protein": 1.1, "fat": 0.3, "carbohydrates": 9.9, "fiber": 0.2, "sodium": 2},
            "面条": {"calories": 109, "protein": 4.5, "fat": 0.5, "carbohydrates": 22, "fiber": 0.8, "sodium": 28},
        }
        
        for item in meal_items:
            food_name = item.get("name", "")
            weight = item.get("weight", 100)
            
            for key, value in food_database.items():
                if key in food_name:
                    for nutrient in nutrition_data:
                        nutrition_data[nutrient] += value.get(nutrient, 0) * (weight / 100)
                    break
        
        return {k: round(v, 1) for k, v in nutrition_data.items()}

    @staticmethod
    def generate_nutrition_advice(bmi: float, requirements: Dict, health_conditions: list) -> str:
        advice = []
        
        bmi_category = NutritionCalculator.get_bmi_category(bmi)
        if bmi_category == "偏瘦":
            advice.append("您的体重偏轻，建议适当增加热量摄入，增加优质蛋白质食物。")
        elif bmi_category == "超重":
            advice.append("您的体重略重，建议控制总热量摄入，增加运动量。")
        elif bmi_category == "肥胖":
            advice.append("您的体重偏重，建议在医生指导下进行减重。")
        else:
            advice.append("您的体重在正常范围内，请继续保持。")
        
        if "糖尿病" in health_conditions:
            advice.append("糖尿病患者：控制碳水化合物摄入，选择低GI食物，少食多餐。")
        if "高血压" in health_conditions:
            advice.append("高血压患者：严格控制盐摄入，每日不超过5g，避免腌制食品。")
        if "高血脂" in health_conditions:
            advice.append("高血脂患者：减少动物脂肪摄入，增加深海鱼类和坚果。")
        if "肾病" in health_conditions:
            advice.append("肾病患者：控制蛋白质摄入量，选择优质蛋白质。")
        
        advice.append(f"每日推荐：热量{requirements['calories']:.0f}千卡，"
                      f"蛋白质{requirements['protein']}g，"
                      f"脂肪{requirements['fat']}g，"
                      f"碳水化合物{requirements['carbohydrates']}g。")
        
        return "\n".join(advice)
