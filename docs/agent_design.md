# Agent Design

The FocusOS agent is stateful and goal-oriented.

## Agent State
- User goal
- Available time
- Energy level
- Historical completion rate
- Previous strategy performance

## Agent Loop
1. Plan
   Generate focus blocks and nudges
2. Act
   Deliver plan to user
3. Observe
   Track completion and feedback
4. Evaluate
   Score plan quality and outcomes
5. Adapt
   Update strategy selection

This loop runs once per day per user.
