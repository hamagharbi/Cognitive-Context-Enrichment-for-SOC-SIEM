import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileInput, History, ShieldAlert } from 'lucide-react';
import { cn } from '@/lib/utils';

const Sidebar = () => {
  const location = useLocation();

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
    { icon: FileInput, label: 'Submit Log', path: '/submit' },
    { icon: History, label: 'Log History', path: '/history' },
  ];

  return (
    <div className="flex h-screen w-64 flex-col border-r bg-card text-card-foreground">
      <div className="flex h-14 items-center border-b px-6">
        <ShieldAlert className="mr-2 h-6 w-6 text-primary" />
        <span className="text-lg font-bold tracking-tight">AI SIEM</span>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              "flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
              location.pathname === item.path ? "bg-accent text-accent-foreground" : "text-muted-foreground"
            )}
          >
            <item.icon className="mr-3 h-5 w-5" />
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="border-t p-4">
        <div className="text-xs text-muted-foreground">
          <p>Connected to Orchestrator</p>
          <p className="mt-1 text-[10px] text-green-500">● Online</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
