"use client"
import { FormInput, Plus } from "lucide-react";
import { OrganizationSwitcher, UserButton } from "@clerk/nextjs";

import { Logo } from "@/components/logo";
import { Button } from "@/components/ui/button";
import { FormPopover } from "@/components/form/form-popover";

import { MobileSidebar } from "./mobile-sidebar";
import { FormPicker } from "@/components/form/form-picker";
import { FormSubmit } from "@/components/form/form-submit";
import { useState } from "react";

export const Navbar = () => {
  const [userQuery, setUserQuery] = useState('');

  const handleSubmit = (event: { preventDefault: () => void; }) => {
      event.preventDefault(); // Prevent default form submission behavior
      
      fetch('http://localhost:5000/query', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({
              user_query: userQuery,
              chat_history: []
          })
      })
      .then(response => response.json())
      .then(data => {
          console.log('Response:', data.response);
          // Handle response data here
      })
      .catch(error => {
          console.error('Error:', error);
          // Handle errors here
      });
  };

  return (
    <nav className="fixed z-50 top-0 px-4 w-full h-14 border-b shadow-sm bg-white flex items-center">
      <MobileSidebar />
      <div className="flex items-center gap-x-4">
        <div className="hidden md:flex">
          <Logo />
        </div>
        <FormPopover align="start" side="bottom" sideOffset={18}>
          <Button variant="primary" size="sm" className="rounded-sm hidden md:block h-auto  py-1.5 px-2">
            Create
          </Button>
        </FormPopover>   
        <form onSubmit={handleSubmit} className="flex gap-2">
            <input 
                type="text" 
                placeholder="Generate your project plan." 
                value={userQuery} 
                onChange={(event) => setUserQuery(event.target.value)} 
                className="outline-none border border-gray-300 rounded-sm h-8 px-2 w-48 md:w-64"
            />
            {/* <Button type="submit" variant="primary" className="rounded-sm hidden md:block h-auto  py-1.5 px-2">Plan</Button> */}
        </form>

        <FormPopover>
          <Button variant="primary" size="sm" className="rounded-sm block md:hidden">
            <Plus className="h-4 w-4" />
          </Button>
        </FormPopover>
      </div>
      <div className="ml-auto flex items-center gap-x-2">
        <OrganizationSwitcher
          hidePersonal
          afterCreateOrganizationUrl="/organization/:id"
          afterLeaveOrganizationUrl="/select-org"
          afterSelectOrganizationUrl="/organization/:id"
          appearance={{
            elements: {
              rootBox: {
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
              },
            },
          }}
        />
        <UserButton
          afterSignOutUrl="/"
          appearance={{
            elements: {
              avatarBox: {
                height: 30,
                width: 30,
              }
            }
          }}
        />
      </div>
    </nav>
  );
};
