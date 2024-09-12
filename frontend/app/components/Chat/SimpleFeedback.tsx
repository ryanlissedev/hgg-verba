import React, { useState } from 'react'
import VerbaButton from "../Navigation/VerbaButton";
import { ThumbsUp, ThumbsDown, X, MessageSquare } from 'lucide-react';

interface SimpleFeedbackProps {
  runId: string;
  onSubmit: (runId: string, feedbackType: string, additionalFeedback: string) => void;
}

export default function SimpleFeedback({ runId, onSubmit }: SimpleFeedbackProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [feedbackType, setFeedbackType] = useState<string | null>(null)
  const [additionalFeedback, setAdditionalFeedback] = useState('')

  const handleFeedback = (type: string) => {
    if (type === 'positive') {
      onSubmit(runId, type, '');
      setIsOpen(false)
    } else {
      setFeedbackType('negative')
    }
  }

  const handleSubmitFeedback = () => {
    if (feedbackType) {
      onSubmit(runId, feedbackType, additionalFeedback);
    }
    setIsOpen(false)
  }

  return (
    <>
      <VerbaButton
        title="Feedback"
        Icon={MessageSquare}
        onClick={() => setIsOpen(true)}
        selected={false}
        disabled={!runId}
      />
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-bg-alt-verba rounded-lg p-6 w-96 relative">
            <VerbaButton
              Icon={X}
              onClick={() => setIsOpen(false)}
              className="absolute right-2 top-2"
              selected={false}
              disabled={false}
            />
            <h2 className="text-xl font-bold mb-4">
              {feedbackType === null ? "Was this helpful?" : "What could we improve?"}
            </h2>
            
            {feedbackType === null ? (
              <div className="flex justify-center space-x-4 mt-4">
                <VerbaButton
                  title="Yes"
                  Icon={ThumbsUp}
                  onClick={() => handleFeedback('positive')}
                  selected={false}
                  disabled={false}
                  selected_color="bg-success-verba"
                />
                <VerbaButton
                  title="No"
                  Icon={ThumbsDown}
                  onClick={() => handleFeedback('negative')}
                  selected={false}
                  disabled={false}
                  selected_color="bg-error-verba"
                />
              </div>
            ) : (
              <>
                <textarea 
                  placeholder="Please provide your feedback..." 
                  value={additionalFeedback}
                  onChange={(e) => setAdditionalFeedback(e.target.value)}
                  className="w-full p-2 rounded bg-bg-verba text-text-verba mt-4"
                />
                <VerbaButton
                  title="Submit Feedback"
                  onClick={handleSubmitFeedback}
                  className="w-full mt-4"
                  selected={false}
                  disabled={false}
                  selected_color="bg-primary-verba"
                />
              </>
            )}
          </div>
        </div>
      )}
    </>
  )
}