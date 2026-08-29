"""
专家匹配服务 - 根据疮疡类型和专家专长匹配最合适的专家
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..models.expert_profile import ExpertProfile


class ExpertMatchingService:
    """专家匹配算法"""

    async def match_experts(
        self,
        db: AsyncSession,
        ulcer_type: str,
        location: str,
        urgency_level: str = "medium",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        匹配合适的专家

        Args:
            db: 数据库会话
            ulcer_type: 疮疡类型（如：印堂疔、鼻疔）
            location: 发病部位（如：头面部、上肢）
            urgency_level: 紧急程度
            limit: 返回专家数量

        Returns:
            匹配的专家列表，按匹配度排序
        """
        # 查询所有活跃且已认证的专家
        query = (
            select(ExpertProfile, User)
            .join(User, ExpertProfile.user_id == User.id)
            .where(
                and_(
                    ExpertProfile.is_active == True,
                    ExpertProfile.is_verified == True,
                    User.is_active == True
                )
            )
        )

        result = await db.execute(query)
        experts = result.all()

        # 计算每个专家的匹配分数
        matched_experts = []
        for expert_profile, user in experts:
            score = self._calculate_match_score(
                expert_profile,
                ulcer_type,
                location,
                urgency_level
            )

            matched_experts.append({
                "expert_id": user.id,
                "name": user.name,
                "hospital": user.hospital,
                "title": expert_profile.title,
                "specialty": expert_profile.specialty,
                "experience_years": expert_profile.experience_years,
                "consultation_fee": expert_profile.consultation_fee,
                "average_rating": expert_profile.average_rating,
                "consultation_count": expert_profile.consultation_count,
                "average_response_minutes": expert_profile.average_response_minutes,
                "match_score": score,
                "match_reason": self._generate_match_reason(
                    expert_profile, ulcer_type, location, score
                )
            })

        # 按匹配分数排序
        matched_experts.sort(key=lambda x: x["match_score"], reverse=True)

        return matched_experts[:limit]

    def _calculate_match_score(
        self,
        expert_profile: ExpertProfile,
        ulcer_type: str,
        location: str,
        urgency_level: str
    ) -> float:
        """
        计算专家匹配分数（0-100）

        评分维度：
        1. 专长匹配度（40分）
        2. 经验水平（20分）
        3. 历史评分（15分）
        4. 响应速度（15分）
        5. 可用性（10分）
        """
        score = 0.0

        # 1. 专长匹配度（40分）
        specialty_score = self._match_specialty(
            expert_profile.specialty,
            expert_profile.expertise_ulcer_types,
            ulcer_type,
            location
        )
        score += specialty_score * 40

        # 2. 经验水平（20分）
        if expert_profile.experience_years:
            experience_score = min(expert_profile.experience_years / 30, 1.0)  # 30年为满分
            score += experience_score * 20

        # 3. 历史评分（15分）
        if expert_profile.average_rating:
            rating_score = expert_profile.average_rating / 5.0  # 5分制
            score += rating_score * 15

        # 4. 响应速度（15分）
        if expert_profile.average_response_minutes:
            # 响应时间越短分数越高，30分钟内为满分
            response_score = max(1 - expert_profile.average_response_minutes / 120, 0)
            score += response_score * 15
        else:
            # 新专家给予中等分数
            score += 7.5

        # 5. 可用性（10分）
        availability_score = self._check_availability(expert_profile)
        score += availability_score * 10

        return round(score, 2)

    def _match_specialty(
        self,
        specialty: Optional[List[str]],
        expertise_ulcer_types: Optional[List[Dict]],
        ulcer_type: str,
        location: str
    ) -> float:
        """
        匹配专长领域（返回0-1的匹配度）
        """
        if not specialty:
            return 0.3  # 无专长信息给予基础分

        score = 0.0

        # 1. 检查是否直接匹配疮疡类型
        if expertise_ulcer_types:
            for expertise in expertise_ulcer_types:
                if expertise.get("ulcer_type") == ulcer_type:
                    # 根据治愈率加权
                    cure_rate = expertise.get("cure_rate", 0.8)
                    score = max(score, 0.9 * cure_rate)

        # 2. 检查部位匹配
        location_keywords = {
            "头面部": ["头面部疮疡", "面部", "头部"],
            "上肢": ["手足疔疮", "四肢疮疡", "上肢"],
            "下肢": ["手足疔疮", "四肢疮疡", "下肢"],
            "躯干": ["躯干疮疡", "胸腹部"]
        }

        if location in location_keywords:
            for keyword in location_keywords[location]:
                if any(keyword in s for s in specialty):
                    score = max(score, 0.7)

        # 3. 通用疮疡专长
        if any("疮疡" in s or "外科" in s for s in specialty):
            score = max(score, 0.5)

        return score

    def _check_availability(self, expert_profile: ExpertProfile) -> float:
        """
        检查专家可用性（返回0-1）
        """
        if not expert_profile.is_active:
            return 0.0

        # TODO: 根据当前时间和专家接诊时间判断
        # TODO: 根据当日已接诊量判断

        # 简化版：活跃且自动接单的专家优先
        if expert_profile.auto_accept:
            return 1.0
        else:
            return 0.7

    def _generate_match_reason(
        self,
        expert_profile: ExpertProfile,
        ulcer_type: str,
        location: str,
        score: float
    ) -> str:
        """生成推荐理由"""
        reasons = []

        # 专长匹配
        if expert_profile.expertise_ulcer_types:
            for expertise in expert_profile.expertise_ulcer_types:
                if expertise.get("ulcer_type") == ulcer_type:
                    count = expertise.get("count", 0)
                    cure_rate = expertise.get("cure_rate", 0)
                    reasons.append(f"擅长{ulcer_type}治疗，已成功诊治{count}例，治愈率{cure_rate*100:.0f}%")
                    break

        # 经验
        if expert_profile.experience_years and expert_profile.experience_years >= 10:
            reasons.append(f"{expert_profile.experience_years}年临床经验")

        # 评分
        if expert_profile.average_rating and expert_profile.average_rating >= 4.5:
            reasons.append(f"患者评分{expert_profile.average_rating:.1f}分")

        # 响应速度
        if expert_profile.average_response_minutes and expert_profile.average_response_minutes < 30:
            reasons.append("快速响应")

        # 综合评价
        if score >= 80:
            reasons.insert(0, "高度匹配")
        elif score >= 60:
            reasons.insert(0, "推荐")

        return "；".join(reasons) if reasons else "综合推荐"


# 全局实例
expert_matching_service = ExpertMatchingService()
