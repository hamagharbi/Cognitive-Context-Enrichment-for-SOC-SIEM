import React, { useState } from 'react';
import { useLogStore } from '@/store/useLogStore';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { NativeSelect } from '@/components/ui/native-select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Loader2, Play, AlertCircle, Trash2 } from 'lucide-react';
import PipelineVisualizer from '@/components/pipeline/PipelineVisualizer';
import AnalysisView from '@/components/analysis/AnalysisView';

import ErrorBoundary from '@/components/ErrorBoundary';

const SubmitLog = () => {
  const [rawLog, setRawLog] = useState('');
  const [source, setSource] = useState('windows_eventlog');
  const { submitLog, currentLog, isLoading, error, clearCurrentLog } = useLogStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rawLog.trim()) return;
    await submitLog(rawLog, source);
  };

  const handleClear = () => {
    setRawLog('');
    clearCurrentLog();
  };

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Left Column: Input */}
      <div className="lg:col-span-1 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Submit Log</CardTitle>
            <CardDescription>Paste a raw log entry to analyze.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Source Type</label>
                <NativeSelect 
                  value={source} 
                  onChange={(e) => setSource(e.target.value)} 
                >
                  <option value="windows_eventlog">Windows Event Log</option>
                  <option value="sysmon">Sysmon</option>
                  <option value="linux_auditd">Linux Auditd</option>
                  <option value="generic_syslog">Generic Syslog</option>
                </NativeSelect>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Raw Log</label>
                <Textarea 
                  value={rawLog}
                  onChange={(e) => setRawLog(e.target.value)}
                  placeholder="Paste log here..."
                  className="min-h-[200px] font-mono text-xs"
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" className="flex-1" disabled={isLoading || !rawLog}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4" />
                      Ingest & Analyze
                    </>
                  )}
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={handleClear}
                  disabled={isLoading || (!rawLog && !currentLog)}
                  title="Clear Analysis"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Pipeline Status */}
        <Card>
          <CardHeader>
            <CardTitle>Pipeline Status</CardTitle>
          </CardHeader>
          <CardContent>
            <PipelineVisualizer log={currentLog} />
          </CardContent>
        </Card>
      </div>

      {/* Right Column: Results */}
      <div className="lg:col-span-2 space-y-6">
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {currentLog ? (
          <ErrorBoundary>
            <AnalysisView log={currentLog} />
          </ErrorBoundary>
        ) : (
          <div className="flex h-full min-h-[400px] items-center justify-center rounded-lg border border-dashed">
            <div className="text-center text-muted-foreground">
              <Play className="mx-auto h-12 w-12 opacity-20" />
              <h3 className="mt-4 text-lg font-semibold">Ready to Analyze</h3>
              <p className="text-sm">Submit a log to see the enrichment pipeline in action.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubmitLog;
