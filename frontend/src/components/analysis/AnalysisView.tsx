import React from 'react';
import { EnrichedAlert } from '@/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { ShieldAlert, Terminal, Brain, Target, Crosshair, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AnalysisViewProps {
  log: EnrichedAlert;
}

const AnalysisView = ({ log }: AnalysisViewProps) => {
  return (
    <div className="space-y-6">
      {/* Summary Section */}
      <Card className="border-l-4 border-l-primary">
        <CardHeader>
          <CardTitle className="flex items-center">
            <ShieldAlert className="mr-2 h-5 w-5 text-primary" />
            Analysis Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-lg font-medium leading-relaxed">{log.summary || "No summary available."}</p>
          
          {log.recommendations && log.recommendations.length > 0 && (
            <div className="mt-4">
              <h4 className="mb-2 text-sm font-semibold text-muted-foreground">Recommendations:</h4>
              <ul className="list-disc pl-5 space-y-1">
                {log.recommendations.map((rec, i) => (
                  <li key={i} className="text-sm">{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Raw & Normalized */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center text-base">
              <Terminal className="mr-2 h-4 w-4" />
              Log Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="mb-1 text-xs font-semibold text-muted-foreground">RAW LOG</h4>
              <div className="rounded-md bg-muted p-3 font-mono text-xs break-all">
                {log.raw_log}
              </div>
            </div>
            {log.normalized && log.normalized.normalized_fields && (
              <div>
                <h4 className="mb-1 text-xs font-semibold text-muted-foreground">NORMALIZED FIELDS</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {Object.entries(log.normalized.normalized_fields).map(([k, v]) => (
                    <div key={k} className="flex flex-col">
                      <span className="text-xs text-muted-foreground">{k}</span>
                      <span className="font-mono text-xs">{String(v)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Semantic & Intent */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-base">
                <Brain className="mr-2 h-4 w-4" />
                Semantic Interpretation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">{log.semantic?.semantic_summary}</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {log.semantic?.semantic_features && Object.entries(log.semantic.semantic_features).map(([k, v]) => (
                  <Badge key={k} variant="secondary">{k}: {String(v)}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-base">
                <Target className="mr-2 h-4 w-4" />
                Intent Classification
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="font-semibold">{log.intent?.intent}</span>
                <Badge variant="outline">{log.intent?.source}</Badge>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{log.intent?.explanation}</p>
              {log.intent?.matched_rules && log.intent.matched_rules.length > 0 && (
                <div className="mt-2">
                  <span className="text-xs text-muted-foreground">Matched Rules: </span>
                  {log.intent.matched_rules.map(rule => (
                    <Badge key={rule} variant="destructive" className="ml-1 text-[10px]">{rule}</Badge>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* MITRE & Risk */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center text-base">
              <Crosshair className="mr-2 h-4 w-4" />
              MITRE ATT&CK
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2 mb-2">
              <Badge className="bg-red-900 text-red-100 hover:bg-red-800">{log.mitre?.technique_id}</Badge>
              <span className="font-bold">{log.mitre?.attack_technique}</span>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm mb-4">
              <div>
                <span className="text-muted-foreground block text-xs">Tactic</span>
                <span>{log.mitre?.tactic}</span>
              </div>
              <div>
                <span className="text-muted-foreground block text-xs">Kill Chain Phase</span>
                <span>{log.mitre?.kill_chain_phase}</span>
              </div>
            </div>
            <p className="text-sm text-muted-foreground">{log.mitre?.explanation}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center text-base">
              <Activity className="mr-2 h-4 w-4" />
              Risk Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center py-4">
              <div className="relative flex items-center justify-center">
                <svg className="h-32 w-32 transform -rotate-90">
                  <circle
                    className="text-muted"
                    strokeWidth="10"
                    stroke="currentColor"
                    fill="transparent"
                    r="58"
                    cx="64"
                    cy="64"
                  />
                  <circle
                    className={cn(
                      "transition-all duration-1000 ease-out",
                      log.risk?.level === 'critical' ? 'text-purple-500' :
                      log.risk?.level === 'high' ? 'text-red-500' :
                      log.risk?.level === 'medium' ? 'text-yellow-500' :
                      'text-green-500'
                    )}
                    strokeWidth="10"
                    strokeDasharray={365}
                    strokeDashoffset={365 - (365 * (log.risk?.score || 0))}
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="transparent"
                    r="58"
                    cx="64"
                    cy="64"
                  />
                </svg>
                <div className="absolute flex flex-col items-center">
                  <span className="text-3xl font-bold">{Math.round((log.risk?.score || 0) * 100)}</span>
                  <span className="text-xs uppercase text-muted-foreground">{log.risk?.level}</span>
                </div>
              </div>
            </div>
            <div className="space-y-2">
              {log.risk?.factors && Object.entries(log.risk.factors).map(([k, v]) => (
                <div key={k} className="flex justify-between text-xs">
                  <span className="text-muted-foreground capitalize">{k.replace(/_/g, ' ')}</span>
                  <span>{String(v)}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AnalysisView;
