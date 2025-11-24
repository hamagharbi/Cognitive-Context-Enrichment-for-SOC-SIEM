import React from 'react';
import { useLogStore } from '@/store/useLogStore';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Eye } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const History = () => {
  const { logs } = useLogStore();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Log History</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Analyzed Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Intent</TableHead>
                <TableHead>Technique</TableHead>
                <TableHead>Risk Score</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.correlation_id}>
                  <TableCell className="font-mono text-xs">
                    {log.normalized?.timestamp ? new Date(log.normalized.timestamp).toLocaleString() : 'N/A'}
                  </TableCell>
                  <TableCell>{log.source}</TableCell>
                  <TableCell>
                    {log.intent?.intent ? (
                      <Badge variant="outline">{log.intent.intent}</Badge>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {log.mitre?.technique_id ? (
                      <div className="flex flex-col">
                        <span className="font-medium">{log.mitre.technique_id}</span>
                        <span className="text-xs text-muted-foreground truncate max-w-[150px]">
                          {log.mitre.attack_technique}
                        </span>
                      </div>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {log.risk ? (
                      <Badge 
                        variant={
                          log.risk.level === 'critical' ? 'risk_critical' : 
                          log.risk.level === 'high' ? 'risk_high' : 
                          log.risk.level === 'medium' ? 'risk_medium' : 
                          'risk_low'
                        }
                      >
                        {log.risk.level.toUpperCase()} ({Math.round(log.risk.score * 100)})
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {logs.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="h-24 text-center">
                    No logs found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default History;
