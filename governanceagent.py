import random

class GovernanceAgent:
    def __init__(self, exploration_rate=0.2):
        self.exploration_rate = exploration_rate
        self.knowledge_base = {}  # proposal_type -> success score

    def propose(self, state):
        # Explore new proposals occasionally
        if random.random() < self.exploration_rate:
            proposal = self.random_proposal()
        else:
            proposal = self.best_proposal(state)
        return proposal

    def random_proposal(self):
        # Random proposal types (e.g., "burn_increase", "burn_decrease", "pause_burn")
        return random.choice(["burn_increase", "burn_decrease", "pause_burn"])

    def best_proposal(self, state):
        # Pick proposal with highest historical success in this state context
        return max(self.knowledge_base, key=self.knowledge_base.get, default="burn_increase")

    def update_knowledge(self, proposal, outcome):
        # Simple reward: +1 for success, -1 for failure
        score = self.knowledge_base.get(proposal, 0)
        self.knowledge_base[proposal] = score + (1 if outcome else -1)
