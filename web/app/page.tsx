"use client";

import { useMutation, useQuery } from "convex/react";
import { useState, useEffect } from "react";
import { api } from "../convex/_generated/api";
import { generatePlan, FocusPlan, GoalInput } from "@/lib/agent";
import { CheckCircle, Clock, Battery, AlertCircle, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Id } from "../convex/_generated/dataModel";

export default function Home() {
  // State
  const [step, setStep] = useState<"input" | "planning" | "view">("input");
  const [goalInput, setGoalInput] = useState<GoalInput>({
    goal_text: "",
    available_minutes: 60,
    energy_level: "medium",
  });
  const [plan, setPlan] = useState<FocusPlan | null>(null);
  const [planId, setPlanId] = useState<Id<"focus_plans"> | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Convex mutations
  const createGoal = useMutation(api.focus.createGoal);
  const savePlanMutation = useMutation(api.focus.savePlan);
  const updateBlockStatus = useMutation(api.focus.updateBlockStatus);
  const latestData = useQuery(api.focus.getLatestGoal);

  // Load latest incomplete plan on startup
  useEffect(() => {
    // Only set if we haven't loaded it yet and data is available
    if (!plan && latestData?.plan && latestData.goal.status !== "completed") {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setPlan(latestData.plan as any);
      setPlanId(latestData.plan._id);
      setStep("view");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [latestData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStep("planning");
    setError(null);

    try {
      // 1. Create Goal
      const goalId = await createGoal(goalInput);

      // 2. Generate Plan (Agent)
      const generatedPlan = await generatePlan(goalInput);

      // 3. Save Plan
      const id = await savePlanMutation({
        goal_id: goalId,
        ...generatedPlan,
        blocks: generatedPlan.blocks.map(b => ({ ...b, completed: false })),
      });

      setPlan(generatedPlan);
      setPlanId(id);
      setStep("view");
    } catch (err) {
      console.error(err);
      setError("Failed to generate plan. Please ensure the agent service is running.");
      setStep("input");
    }
  };

  const toggleBlock = async (index: number, completed: boolean) => {
    if (!planId || !plan) return;
    
    // Optimistic update
    const newBlocks = [...plan.blocks];
    newBlocks[index].completed = completed;
    setPlan({ ...plan, blocks: newBlocks });

    await updateBlockStatus({
      plan_id: planId,
      block_index: index,
      completed,
    });
  };

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100 p-4 md:p-8 flex justify-center">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <header className="mb-12 text-center">
          <h1 className="text-3xl font-bold tracking-tight mb-2 flex items-center justify-center gap-2">
            <CheckCircle className="w-8 h-8 text-emerald-500" />
            FocusOS
          </h1>
          <p className="text-neutral-400">AI-powered focus & habit coach</p>
        </header>

        {/* Error Message */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-200 p-4 rounded-lg mb-8 flex gap-3 items-center">
            <AlertCircle className="w-5 h-5" />
            <p>{error}</p>
          </div>
        )}

        {/* Step: Input */}
        {step === "input" && (
          <form onSubmit={handleSubmit} className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="space-y-4">
              <label className="block text-lg font-medium text-neutral-200">
                What is your main goal for today?
              </label>
              <textarea
                value={goalInput.goal_text}
                onChange={(e) => setGoalInput({ ...goalInput, goal_text: e.target.value })}
                className="w-full bg-neutral-900 border border-neutral-800 rounded-xl p-4 text-lg focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 outline-none transition-all placeholder:text-neutral-600"
                placeholder="e.g. Finish the API integration and write docs..."
                rows={3}
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <label className="block text-neutral-300 flex items-center gap-2">
                  <Clock className="w-4 h-4" /> Available Time
                </label>
                <div className="flex gap-2">
                  {[30, 60, 120, 240].map((min) => (
                    <button
                      key={min}
                      type="button"
                      onClick={() => setGoalInput({ ...goalInput, available_minutes: min })}
                      className={cn(
                        "px-4 py-2 rounded-lg text-sm font-medium transition-colors border",
                        goalInput.available_minutes === min
                          ? "bg-emerald-500/10 border-emerald-500 text-emerald-400"
                          : "bg-neutral-900 border-neutral-800 text-neutral-400 hover:bg-neutral-800"
                      )}
                    >
                      {min < 60 ? `${min}m` : `${min / 60}h`}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <label className="block text-neutral-300 flex items-center gap-2">
                  <Battery className="w-4 h-4" /> Energy Level
                </label>
                <div className="flex gap-2">
                  {(["low", "medium", "high"] as const).map((level) => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => setGoalInput({ ...goalInput, energy_level: level })}
                      className={cn(
                        "px-4 py-2 rounded-lg text-sm font-medium transition-colors border capitalize",
                        goalInput.energy_level === level
                          ? "bg-blue-500/10 border-blue-500 text-blue-400"
                          : "bg-neutral-900 border-neutral-800 text-neutral-400 hover:bg-neutral-800"
                      )}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-emerald-500 hover:bg-emerald-400 text-neutral-950 font-bold py-4 rounded-xl transition-all flex items-center justify-center gap-2 group"
            >
              Generate Plan
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </form>
        )}

        {/* Step: Planning (Loading) */}
        {step === "planning" && (
          <div className="flex flex-col items-center justify-center py-20 space-y-6 animate-in fade-in duration-500">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
            </div>
            <p className="text-neutral-400 animate-pulse">Consulting the agent...</p>
          </div>
        )}

        {/* Step: View Plan */}
        {step === "view" && plan && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Evaluation Score Card */}
            {plan.evaluation && (
              <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider">Plan Quality</h3>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl font-bold text-emerald-400">{plan.evaluation.overall_score}</span>
                    <span className="text-neutral-500 text-sm">/ 10</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Clarity</span>
                    <span className="text-neutral-200">{plan.evaluation.task_clarity.score}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Realism</span>
                    <span className="text-neutral-200">{plan.evaluation.workload_realism.score}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Alignment</span>
                    <span className="text-neutral-200">{plan.evaluation.goal_alignment.score}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Motivation</span>
                    <span className="text-neutral-200">{plan.evaluation.motivation_quality.score}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Focus Blocks */}
            <div className="space-y-4">
              {plan.blocks.map((block, idx) => (
                <div
                  key={idx}
                  className={cn(
                    "group relative border rounded-xl p-5 transition-all",
                    block.completed
                      ? "bg-neutral-900/30 border-neutral-800 opacity-60"
                      : "bg-neutral-900 border-neutral-800 hover:border-neutral-700"
                  )}
                >
                  <div className="flex items-start gap-4">
                    <button
                      onClick={() => toggleBlock(idx, !block.completed)}
                      className={cn(
                        "mt-1 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors",
                        block.completed
                          ? "bg-emerald-500 border-emerald-500 text-neutral-950"
                          : "border-neutral-600 hover:border-emerald-500"
                      )}
                    >
                      {block.completed && <CheckCircle className="w-4 h-4" />}
                    </button>
                    
                    <div className="flex-1 space-y-1">
                      <div className="flex justify-between items-start">
                        <p className={cn(
                          "font-medium text-lg leading-tight transition-all",
                          block.completed ? "text-neutral-500 line-through" : "text-neutral-200"
                        )}>
                          {block.task}
                        </p>
                        <span className="text-xs font-mono text-neutral-500 bg-neutral-950 px-2 py-1 rounded">
                          {block.duration_min}m
                        </span>
                      </div>
                      <p className="text-sm text-neutral-400 italic">&quot;{block.nudge}&quot;</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-8 border-t border-neutral-900 text-center">
              <button
                onClick={() => setStep("input")}
                className="text-sm text-neutral-500 hover:text-neutral-300 transition-colors"
              >
                Start a new day
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
