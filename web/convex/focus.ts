import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// === Mutations ===

export const createGoal = mutation({
  args: {
    goal_text: v.string(),
    available_minutes: v.number(),
    energy_level: v.string(),
  },
  handler: async (ctx, args) => {
    const goalId = await ctx.db.insert("daily_goals", {
      ...args,
      status: "pending",
      created_at: Date.now(),
    });
    return goalId;
  },
});

export const savePlan = mutation({
  args: {
    goal_id: v.id("daily_goals"),
    strategy_id: v.string(),
    prompt_version: v.string(),
    total_minutes: v.number(),
    blocks: v.array(
      v.object({
        order: v.number(),
        duration_min: v.number(),
        task: v.string(),
        nudge: v.string(),
        completed: v.boolean(),
      })
    ),
    evaluation: v.optional(
      v.object({
        task_clarity: v.object({ score: v.number(), reasoning: v.string() }),
        workload_realism: v.object({ score: v.number(), reasoning: v.string() }),
        goal_alignment: v.object({ score: v.number(), reasoning: v.string() }),
        motivation_quality: v.object({ score: v.number(), reasoning: v.string() }),
        overall_score: v.number(),
      })
    ),
  },
  handler: async (ctx, args) => {
    // Save the plan
    const planId = await ctx.db.insert("focus_plans", {
      ...args,
      created_at: Date.now(),
    });

    // Update goal status
    await ctx.db.patch(args.goal_id, { status: "planned" });

    return planId;
  },
});

export const updateBlockStatus = mutation({
  args: {
    plan_id: v.id("focus_plans"),
    block_index: v.number(),
    completed: v.boolean(),
  },
  handler: async (ctx, args) => {
    const plan = await ctx.db.get(args.plan_id);
    if (!plan) throw new Error("Plan not found");

    const newBlocks = [...plan.blocks];
    newBlocks[args.block_index].completed = args.completed;

    await ctx.db.patch(args.plan_id, { blocks: newBlocks });
  },
});

export const submitFeedback = mutation({
  args: {
    plan_id: v.id("focus_plans"),
    completed: v.boolean(),
    perceived_difficulty: v.number(),
    usefulness_score: v.number(),
    free_text: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    await ctx.db.insert("feedback", {
      ...args,
      created_at: Date.now(),
    });
    
    // Also mark goal as completed if feedback is submitted
    const plan = await ctx.db.get(args.plan_id);
    if (plan) {
      await ctx.db.patch(plan.goal_id, { status: "completed" });
    }
  },
});

// === Queries ===

export const getLatestGoal = query({
  handler: async (ctx) => {
    const goal = await ctx.db.query("daily_goals").order("desc").first();
    if (!goal) return null;

    // If there's a plan, fetch it too
    let plan = null;
    if (goal.status !== "pending") {
      plan = await ctx.db
        .query("focus_plans")
        .withIndex("by_goal_id", (q) => q.eq("goal_id", goal._id))
        .first();
    }

    return { goal, plan };
  },
});
