import React from 'react';
import { useLogStore } from '@/store/useLogStore';
import StatCard from '@/components/dashboard/StatCard';
import { Shield, AlertTriangle, Activity, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const Dashboard = () => {
  const { logs } = useLogStore();

  const totalLogs = logs.length;
  const criticalAlerts = logs.filter(l => l.risk?.level === 'critical').length;
  const highAlerts = logs.filter(l => l.risk?.level === 'high').length;
  const avgRisk = logs.length > 0 
    ? (logs.reduce((acc, curr) => acc + (curr.risk?.score || 0), 0) / logs.length * 100).toFixed(1) 
    : "0";

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Logs Analyzed"
          value={totalLogs}
          icon={FileText}
          description="Since last reset"
        />
        <StatCard
          title="Critical Threats"
          value={criticalAlerts}
          icon={AlertTriangle}
          description="Requires immediate attention"
          trend={criticalAlerts > 0 ? "+2" : undefined}
        />
        <StatCard
          title="High Risk Events"
          value={highAlerts}
          icon={Shield}
          description="Potential security incidents"
        />
        <StatCard
          title="Average Risk Score"
          value={`${avgRisk}%`}
          icon={Activity}
          description="Overall threat landscape"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-8">
              {logs.slice(0, 5).map((log) => (
                <div key={log.correlation_id} className="flex items-center">
                  <div className="ml-4 space-y-1">
                    <p className="text-sm font-medium leading-none">{log.intent?.intent || "Unknown Intent"}</p>
                    <p className="text-sm text-muted-foreground">
                      {log.mitre?.attack_technique || "No Technique Mapped"}
                    </p>
                  </div>
                  <div className="ml-auto font-medium">
                    <Badge 
                      variant={
                        log.risk?.level === 'critical' ? 'destructive' : 
                        log.risk?.level === 'high' ? 'destructive' : 
                        'secondary'
                      }
                    >
                      {log.risk?.level.toUpperCase()}
                    </Badge>
                  </div>
                </div>
              ))}
              {logs.length === 0 && (
                <div className="text-center text-muted-foreground py-8">
                  No logs analyzed yet. Submit a log to see activity.
                </div>
              )}
            </div>
          </CardContent>
        </Card>
        
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Top Techniques</CardTitle>
          </CardHeader>
          <CardContent>
             {/* Placeholder for a chart or list */}
             <div className="space-y-4">
                {/* Mock data for visualization */}
                {['T1059 - Command and Scripting Interpreter', 'T1003 - OS Credential Dumping', 'T1078 - Valid Accounts'].map((tech, i) => (
                  <div key={i} className="flex items-center">
                    <div className="w-full space-y-1">
                      <p className="text-sm font-medium leading-none">{tech}</p>
                      <div className="h-2 w-full rounded-full bg-secondary mt-2">
                        <div className="h-2 rounded-full bg-primary" style={{ width: `${80 - (i * 20)}%` }} />
                      </div>
                    </div>
                  </div>
                ))}
             </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
