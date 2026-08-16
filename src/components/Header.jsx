import { Settings, User } from "lucide-react";

function Header() {
  return (
    <header className="h-16 bg-blue-900 text-white flex items-center justify-between px-8 shadow-md">

      <h1 className="text-2xl font-bold">
        OptimizationChat
      </h1>

      <div className="flex gap-3">

        <button className="bg-white p-2 rounded-lg text-slate-700 hover:bg-slate-200">
          <Settings size={20} />
        </button>

        <button className="bg-white p-2 rounded-lg text-slate-700 hover:bg-slate-200">
          <User size={20} />
        </button>

      </div>

    </header>
  );
}

export default Header;