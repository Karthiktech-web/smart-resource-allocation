import { signOut } from 'firebase/auth';
import type { User } from 'firebase/auth';
import { auth } from '../../lib/firebase';
import { LogOut, Bell } from 'lucide-react';

interface HeaderProps {
  user: User | null;
}

export default function Header({ user }: HeaderProps) {
  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      
      {/* Title */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800">
          Smart Resource Allocation
        </h2>
        <p className="text-xs text-gray-400">
          AI-Powered Volunteer Coordination for Social Impact
        </p>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-4">

        {/* Notification Bell */}
        <button className="relative p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-50">
          <Bell size={20} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        {/* User Info */}
        <div className="flex items-center gap-3">
          {user?.photoURL ? (
            <img
              src={user.photoURL}
              alt="Profile"
              className="w-8 h-8 rounded-full object-cover"
            />
          ) : (
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-blue-700">
                {user?.displayName?.charAt(0)?.toUpperCase() || 'U'}
              </span>
            </div>
          )}

          <div className="hidden md:block">
            <p className="text-sm font-medium text-gray-700">
              {user?.displayName || 'User'}
            </p>
            <p className="text-xs text-gray-400">
              {user?.email || ''}
            </p>
          </div>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="p-2 text-gray-400 hover:text-red-500 rounded-lg hover:bg-gray-50 transition-colors"
          title="Logout"
        >
          <LogOut size={18} />
        </button>

      </div>
    </header>
  );
}