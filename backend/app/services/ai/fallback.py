"""Deterministic Fallback Provider for TouchGrass AI.
Provides safe, time-matched, activity-matched missions when AI is unavailable or fails validation.
"""

from typing import Dict, Any, List
from app.services.ai.base import BaseAIProvider
from app.schemas.plan import MissionPlan

FALLBACK_MISSIONS: Dict[str, Dict[str, Any]] = {
    "walking": {
        "title": "{duration}-Minute Neighborhood Discovery Walk",
        "steps_pool": {
            15: [
                "Step outside and put your phone completely in your pocket or bag.",
                "Walk briskly away from your screen for 6 minutes in an unfamiliar local direction.",
                "Stop at a quiet sidewalk or path and take three deep breaths.",
                "Turn back and walk deliberately, noticing five natural colors around you.",
            ],
            30: [
                "Leave your phone in your pocket on silent mode.",
                "Walk at a steady, relaxing pace for 12 minutes towards a green space or quiet street.",
                "Notice three architecture or landscaping details you have never spotted before.",
                "Find a bench or open spot to pause for 5 minutes without touching any device.",
                "Return at a relaxed pace, taking in the ambient sounds.",
            ],
            60: [
                "Stash your phone and head out towards your nearest park, trail, or neighborhood greenway.",
                "Walk outward for 25 minutes, keeping an upright posture and relaxed stride.",
                "Observe the shifting sunlight, tree canopies, and bird songs along the route.",
                "Rest outdoors for 10 minutes simply looking around at the horizon.",
                "Complete the return loop, feeling the physical difference of disconnecting.",
            ],
        },
        "safety_note": "Stick to designated pedestrian sidewalks, remain alert at street crossings, and hydrate.",
    },
    "nature": {
        "title": "{duration}-Minute Mindful Nature Observation",
        "steps_pool": {
            15: [
                "Step into your nearest yard, garden, park, or tree-lined street.",
                "Find three distinctly different types of leaves or plant textures.",
                "Close your eyes for two minutes and identify at least two natural sounds.",
                "Touch the bark of a nearby tree or brush your hand across grass or leaves.",
            ],
            30: [
                "Head outside to a park, garden, or quiet natural patch.",
                "Walk for 10 minutes without looking at any screen.",
                "Locate and observe three different plant or tree species up close.",
                "Notice one subtle natural sound (wind, birds, rustling leaves) you normally ignore.",
                "Sit outdoors quietly for five minutes before walking back.",
            ],
            60: [
                "Travel to a local public park, botanical garden, or nature preserve.",
                "Begin a slow, observant nature exploration walk for 25 minutes.",
                "Catalog mentally five wild elements: moss, leaf patterns, cloud shapes, stone textures, or insects.",
                "Spend 15 peaceful minutes sitting under a tree canopy with your device tucked away.",
                "Conclude with a calm 15-minute nature stroll back.",
            ],
        },
        "safety_note": "Stay on marked public trails, do not eat wild plants or fungi, and respect local flora.",
    },
    "photography": {
        "title": "{duration}-Minute Outdoor Visual Eye Challenge",
        "steps_pool": {
            15: [
                "Step outside into natural light with a single visual focus in mind.",
                "Look up and capture one interesting pattern created by tree branches or shadows.",
                "Look down and find an intriguing ground texture (moss, cobblestone, autumn leaves).",
                "Put your camera/phone immediately away and absorb the scene with your own eyes for 5 minutes.",
            ],
            30: [
                "Venture outdoors to an open public area during good ambient light.",
                "Look for high-contrast shadows or natural geometry without rushing.",
                "Frame exactly three deliberate outdoor composition photos (texture, depth, sky).",
                "Once captured, pocket your phone completely for the remaining 15 minutes of quiet outdoor walking.",
            ],
            60: [
                "Take a creative outdoor photo walk around your neighborhood or local park.",
                "Spend 25 minutes seeking out micro-details: raindrops on leaves, weathered wood, or shifting light.",
                "Take no more than five intentional, carefully framed outdoor shots.",
                "Spend the final 25 minutes walking without holding or checking your device.",
            ],
        },
        "safety_note": "Never view the screen while walking across streets, stay aware of your surroundings at all times.",
    },
    "exercise": {
        "title": "{duration}-Minute Fresh-Air Body & Movement Reset",
        "steps_pool": {
            15: [
                "Step outside into the open air and do 2 minutes of gentle shoulder and neck rolls.",
                "Brisk walk for 5 minutes to get your heart rate up.",
                "Perform 15 gentle bodyweight squats or standing calf raises near a park bench.",
                "Take 3 minutes of deep outdoor diaphragmatic breathing before returning.",
            ],
            30: [
                "Put on comfortable shoes and head outside to an open, flat public area.",
                "Warm up with 8 minutes of brisk walking and arm swings in the fresh breeze.",
                "Complete 3 rounds: 10 bodyweight squats, 20 high-knees march, and 30 seconds calf stretches.",
                "Walk calmly for 10 minutes to cool down, focusing on rhythmic breathing.",
            ],
            60: [
                "Head to a public park, trail, or outdoor fitness path.",
                "Brisk walking or light jogging warm-up for 15 minutes in the open air.",
                "Engage in an outdoor functional movement circuit (lunges, step-ups on park ledges, torso twists) for 20 minutes.",
                "Dedicate 15 minutes to comprehensive standing stretches under the open sky.",
                "Cool down with a 10-minute relaxing stroll.",
            ],
        },
        "safety_note": "Exercise at your own pace, wear appropriate footwear, avoid slick surfaces, and drink water.",
    },
    "social": {
        "title": "{duration}-Minute Outdoor Connection Mission",
        "steps_pool": {
            15: [
                "Step outside into the open air with a friend or neighbor (or invite one along).",
                "Agree that all phones stay zipped in pockets during the entire outing.",
                "Walk together around the block discussing what you're noticing in the weather and neighborhood.",
                "Share one non-digital thought or memory before finishing.",
            ],
            30: [
                "Meet up outdoors at a park, bench, or open walking path.",
                "Place all phones away on 'Do Not Disturb'.",
                "Walk shoulder-to-shoulder for 15 minutes, listening and conversing openly.",
                "Pause at an outdoor overlook or green spot for 10 minutes of screen-free conversation.",
                "Return feeling refreshed from genuine real-world face-to-face interaction.",
            ],
            60: [
                "Gather a companion or group for an extended outdoor expedition.",
                "Keep devices tucked away; embark on a continuous 40-minute walk through public parks or streets.",
                "Take turns pointing out unusual trees, animals, or local history points along the path.",
                "Sit outdoors together for 15 minutes sharing an outdoor refreshment or calm reflection.",
            ],
        },
        "safety_note": "Respect public space courtesy, cross roadways together safely, and look out for each other.",
    },
}


class DeterministicFallbackProvider(BaseAIProvider):
    """Deterministic fallback mission provider matching duration, activity, difficulty, and mode."""

    @property
    def provider_name(self) -> str:
        return "fallback"

    async def generate_outdoor_mission(self, preferences: Dict[str, Any]) -> MissionPlan:
        duration = preferences.get("duration_minutes", 30)
        activity = preferences.get("activity_type", "nature")
        difficulty = preferences.get("difficulty", "easy")
        mode = preferences.get("mode", "solo")

        # Fallback to 'nature' or 30 mins if unexpected value
        activity_data = FALLBACK_MISSIONS.get(activity, FALLBACK_MISSIONS["nature"])
        title_template = activity_data["title"]
        title = title_template.format(duration=duration)
        if mode == "friends":
            title += " (Shared)"

        duration_steps = activity_data["steps_pool"].get(duration, activity_data["steps_pool"][30])
        steps: List[str] = list(duration_steps)

        # Minor difficulty adjustment if hard
        if difficulty == "hard" and len(steps) >= 3:
            steps[1] = steps[1] + " (Maintain an energetic, brisk pace throughout.)"

        safety_note = activity_data["safety_note"]
        if mode == "friends":
            safety_note += " Stay together as a group and be mindful of other pedestrians."

        return MissionPlan(
            title=title,
            duration_minutes=duration,
            activity_type=activity,
            difficulty=difficulty,
            mode=mode,
            steps=steps,
            safety_note=safety_note,
        )
