import { Logo } from "@/components/logo";
import { Button } from "@/components/ui/button";

export const Footer = () => {
  return (
    <div className="fixed bottom-0 w-full p-2 border-t bg-slate-100">
      <div className="md:max-w-screen-2xl mx-auto flex items-center w-full justify-between">
        <Button size="sm" variant="ghost" className="text-neutral-500">
          Contact US
        </Button>
        <Button size="sm" variant="ghost" className="text-neutral-500">
          Private Policy
        </Button>
        <Button size="sm" variant="ghost" className="text-neutral-500">
          Terms of Services
        </Button>
      </div>
    </div>
  );
};
