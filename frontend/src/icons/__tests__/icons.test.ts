import { CheckIcon } from '../CheckIcon'
import { LoadingIndicatorIcon } from '../LoadingIndicatorIcon'
import { PdfIcon } from '../PdfIcon'
import UploadIcon from '../UploadIcon'

describe('Icon components', () => {
  it('should render CheckIcon without errors', () => {
    expect(() => CheckIcon()).not.toThrow()
  })

  it('should render LoadingIndicatorIcon without errors', () => {
    expect(() => LoadingIndicatorIcon()).not.toThrow()
  })

  it('should render PdfIcon without errors', () => {
    expect(() => PdfIcon()).not.toThrow()
  })

  it('should render UploadIcon without errors', () => {
    expect(() => UploadIcon()).not.toThrow()
  })
})

