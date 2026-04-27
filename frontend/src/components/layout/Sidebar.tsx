import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Upload,
  AlertTriangle,
  FolderOpen,
  Users,
  BarChart3,
  Map,
  UserCircle,
  FileText,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

// Type for nav items (BEST PRACTICE)
type NavItem = {
  to: string;
  icon: LucideIcon;
  label: string;
};

const navItems: NavItem[] = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/ingest', icon: Upload, label: 'Ingest Data' },
  { to: '/needs', icon: AlertTriangle, label: 'Needs' },
  { to: '/programs', icon: FolderOpen, label: 'Programs' },
  { to: '/allocate', icon: Users, label: 'Allocate' },
  { to: '/impact', icon: BarChart3, label: 'Impact' },
  { to: '/reports', icon: FileText, label: 'Reports' },
  { to: '/volunteers', icon: UserCircle, label: 'Volunteers' },
];

type SidebarProps = {
  onLinkClick?: () => void;
};

export default function Sidebar({ onLinkClick }: SidebarProps) {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen flex flex-col">
      
      {/* Logo / Title */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Map size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-gray-800">
              Smart Resource
            </h1>
            <p className="text-xs text-gray-400">
              Allocation Platform
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onLinkClick}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
              }`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-100">
        <p className="text-xs text-gray-400 text-center">
          Google Solution Challenge 2026
        </p>
      </div>
    </aside>
  );
}