import React from 'react';
import { EnrichedAlert } from '@/types';
import { CheckCircle2, Circle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PipelineVisualizerProps {
  log: EnrichedAlert | null;
}

const PipelineVisualizer = ({ log }: PipelineVisualizerProps) => {
  const steps = [
    { id: 'ingest', label: 'Log Ingestion', status: log?.normalized ? 'success' : 'pending' },
    { id: 'normalize', label: 'Normalization', status: log?.normalized ? 'success' : 'pending' },
    { id: 'semantic', label: 'Semantic Interpreter', status: log?.semantic ? 'success' : 'pending' },
    { id: 'intent', label: 'Intent Classifier', status: log?.intent ? 'success' : 'pending' },
    { id: 'mitre', label: 'MITRE Reasoner', status: log?.mitre ? 'success' : 'pending' },
    { id: 'risk', label: 'Risk Engine', status: log?.risk ? 'success' : 'pending' },
  ];

  return (
    <div className="relative flex flex-col space-y-4">
      {steps.map((step, index) => (
        <div key={step.id} className="flex items-center relative z-10">
          <div className={cn(
            "flex h-8 w-8 items-center justify-center rounded-full border-2",
            step.status === 'success' ? "border-green-500 bg-green-500/10 text-green-500" : "border-muted-foreground text-muted-foreground"
          )}>
            {step.status === 'success' ? <CheckCircle2 className="h-5 w-5" /> : <Circle className="h-5 w-5" />}
          </div>
          <div className="ml-4">
            <p className={cn(
              "text-sm font-medium",
              step.status === 'success' ? "text-foreground" : "text-muted-foreground"
            )}>
              {step.label}
            </p>
          </div>
          {index < steps.length - 1 && (
            <div className="absolute left-4 top-8 h-4 w-0.5 bg-border -ml-[1px] -z-10" />
          )}
        </div>
      ))}
    </div>
  );
};

export default PipelineVisualizer;
