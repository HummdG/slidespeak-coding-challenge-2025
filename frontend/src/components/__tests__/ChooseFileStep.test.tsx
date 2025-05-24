// frontend/src/components/__tests__/ChooseFileStep.test.tsx
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";
import { ChooseFileStep } from "../ChooseFileStep";

describe("ChooseFileStep", () => {
  const mockOnSelect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Rendering", () => {
    it("renders the drag and drop area", () => {
      render(<ChooseFileStep onSelect={mockOnSelect} />);

      expect(
        screen.getByText(/drag and drop a powerpoint file/i)
      ).toBeInTheDocument();
      expect(screen.getByText(/choose file/i)).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /choose file/i })
      ).toBeInTheDocument();
    });

    it("renders the upload icon", () => {
      render(<ChooseFileStep onSelect={mockOnSelect} />);

      const uploadIcon = screen
        .getByRole("button", { name: /choose file/i })
        .closest("div")
        ?.querySelector("svg");
      expect(uploadIcon).toBeInTheDocument();
    });

    it("has proper styling classes", () => {
      const { container } = render(<ChooseFileStep onSelect={mockOnSelect} />);

      const dropArea = container.querySelector(".border-dashed");
      expect(dropArea).toHaveClass(
        "border-2",
        "border-dashed",
        "border-gray-300",
        "rounded-2xl"
      );
    });
  });

  describe("File Input Interaction", () => {
    it("triggers file selection when choose file button is clicked", async () => {
      const user = userEvent.setup();
      render(<ChooseFileStep onSelect={mockOnSelect} />);

      const fileInput = screen.getByRole("button", { name: /choose file/i });
      await user.click(fileInput);

      // The actual file input should be hidden but accessible
      const hiddenInput = document.querySelector('input[type="file"]');
      expect(hiddenInput).toBeInTheDocument();
      expect(hiddenInput).toHaveAttribute("accept", ".pptx");
    });

    it("calls onSelect when a valid .pptx file is selected", async () => {
      const user = userEvent.setup();
      render(<ChooseFileStep onSelect={mockOnSelect} />);

      const file = new File(["test content"], "test.pptx", {
        type: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      });

      const fileInput = document.querySelector(
        'input[type="file"]'
      ) as HTMLInputElement;
      await user.upload(fileInput, file);

      expect(mockOnSelect).toHaveBeenCalledWith(file);
    });

    it("does not call onSelect when no file is selected", async () => {
      const user = userEvent.setup();
      render(<ChooseFileStep onSelect={mockOnSelect} />);

      const fileInput = document.querySelector(
        'input[type="file"]'
      ) as HTMLInputElement;
      fireEvent.change(fileInput, { target: { files: [] } });

      expect(mockOnSelect).not.toHaveBeenCalled();
    });
  });

  describe("Drag and Drop Functionality", () => {
    it("prevents default behavior on drag over", () => {
      const { container } = render(<ChooseFileStep onSelect={mockOnSelect} />);
      const dropArea = container.querySelector(".border-dashed") as HTMLElement;

      const dragOverEvent = new DragEvent("dragover", { bubbles: true });
      const preventDefaultSpy = jest.spyOn(dragOverEvent, "preventDefault");

      fireEvent(dropArea, dragOverEvent);

      expect(preventDefaultSpy).toHaveBeenCalled();
    });

    it("handles file drop with valid .pptx file", () => {
      const { container } = render(<ChooseFileStep onSelect={mockOnSelect} />);
      const dropArea = container.querySelector(".border-dashed") as HTMLElement;

      const file = new File(["test content"], "test.pptx", {
        type: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      });

      const dropEvent = new DragEvent("drop", { bubbles: true });
      Object.defineProperty(dropEvent, "dataTransfer", {
        value: {
          files: [file],
        },
      });

      const preventDefaultSpy = jest.spyOn(dropEvent, "preventDefault");

      fireEvent(dropArea, dropEvent);

      expect(preventDefaultSpy).toHaveBeenCalled();
      expect(mockOnSelect).toHaveBeenCalledWith(file);
    });

    it("ignores non-.pptx files on drop", () => {
      const { container } = render(<ChooseFileStep onSelect={mockOnSelect} />);
      const dropArea = container.querySelector(".border-dashed") as HTMLElement;

      const file = new File(["test content"], "test.pdf", {
        type: "application/pdf",
      });

      const dropEvent = new DragEvent("drop", { bubbles: true });
      Object.defineProperty(dropEvent, "dataTransfer", {
        value: {
          files: [file],
        },
      });

      fireEvent(dropArea, dropEvent);

      expect(mockOnSelect).not.toHaveBeenCalled();
    });

    it("ignores drop when no files are present", () => {
      const { container } = render(<ChooseFileStep onSelect={mockOnSelect} />);
      const dropArea = container.querySelector(".border-dashed") as HTMLElement;

      const dropEvent = new DragEvent("drop", { bubbles: true });
      Object.defineProperty(dropEvent, "dataTransfer", {
        value: {
          files: [],
        },
      });

      fireEvent(dropArea, dropEvent);

      expect(mockOnSelect).not.toHaveBeenCalled();
    });
  });

  describe("Accessibility", () => {
    it("has proper accessibility attributes", () => {
      render(<ChooseFileStep onSelect={mockOnSelect} />);

      const fileInput = document.querySelector('input[type="file"]');
      const label = screen.getByText(/choose file/i);

      expect(fileInput).toHaveAttribute("id", "pptx-input");
      expect(label).toHaveAttribute("for", "pptx-input");
    });

    it("has proper ARIA labels and roles", () => {
      render(<ChooseFileStep onSelect={mockOnSelect} />);

      const button = screen.getByRole("button", { name: /choose file/i });
      expect(button).toBeInTheDocument();
    });
  });

  describe("Edge Cases", () => {
    it("handles multiple files but only selects the first .pptx", () => {
      const { container } = render(<ChooseFileStep onSelect={mockOnSelect} />);
      const dropArea = container.querySelector(".border-dashed") as HTMLElement;

      const pptxFile = new File(["test content"], "test.pptx", {
        type: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      });
      const pdfFile = new File(["test content"], "test.pdf", {
        type: "application/pdf",
      });

      const dropEvent = new DragEvent("drop", { bubbles: true });
      Object.defineProperty(dropEvent, "dataTransfer", {
        value: {
          files: [pptxFile, pdfFile],
        },
      });

      fireEvent(dropArea, dropEvent);

      expect(mockOnSelect).toHaveBeenCalledWith(pptxFile);
      expect(mockOnSelect).toHaveBeenCalledTimes(1);
    });

    it("handles case-insensitive file extension matching", () => {
      const { container } = render(<ChooseFileStep onSelect={mockOnSelect} />);
      const dropArea = container.querySelector(".border-dashed") as HTMLElement;

      const file = new File(["test content"], "test.PPTX", {
        type: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      });

      const dropEvent = new DragEvent("drop", { bubbles: true });
      Object.defineProperty(dropEvent, "dataTransfer", {
        value: {
          files: [file],
        },
      });

      fireEvent(dropArea, dropEvent);

      expect(mockOnSelect).toHaveBeenCalledWith(file);
    });
  });
});
