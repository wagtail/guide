import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vite-plus/test';
import { debounce } from '.';

describe('debounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('only calls the callback once after the wait has elapsed', () => {
    const callback = vi.fn();
    const debounced = debounce(callback, 150);

    debounced('a');
    debounced('b');
    debounced('c');

    expect(callback).not.toHaveBeenCalled();

    vi.advanceTimersByTime(149);
    expect(callback).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1);
    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('passes the arguments from the last call through', () => {
    const callback = vi.fn();
    const debounced = debounce(callback, 150);

    debounced('a');
    debounced('b');

    vi.advanceTimersByTime(150);

    expect(callback).toHaveBeenCalledWith('b');
  });
});
