import React from 'react';
import { Button } from "@/components/ui/button";

interface InterestsSelectionProps {
  tags: string[];
  selectedInterests: string[];
  onTagSelection?: (tag: string) => void;  // Optional function to handle tag selection
  isEditable: boolean;  // Prop to determine if interests can be edited
}

const InterestsSelection: React.FC<InterestsSelectionProps> = ({ tags, selectedInterests, onTagSelection, isEditable }) => {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-2">
        {tags.map(tag => (
          <Button
            key={tag}
            variant={selectedInterests.includes(tag) ? 'default' : 'outline'}
            onClick={isEditable ? () => onTagSelection?.(tag) : undefined}  // Only allow selection if editable
            disabled={!isEditable}  // Disable button if not editable
          >
            {tag}
          </Button>
        ))}
      </div>
    </div>
  );
};

export default InterestsSelection;
