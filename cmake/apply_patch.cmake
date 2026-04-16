# Reset the working tree to the fetched commit before applying so the patch
# is idempotent across repeated FetchContent configure runs.
execute_process(
  COMMAND "${GIT_EXECUTABLE}" checkout HEAD -- .
  WORKING_DIRECTORY "${SOURCE_DIR}"
  OUTPUT_QUIET ERROR_QUIET
)

execute_process(
  COMMAND "${GIT_EXECUTABLE}" apply "${PATCH_FILE}"
  WORKING_DIRECTORY "${SOURCE_DIR}"
  RESULT_VARIABLE result
  OUTPUT_VARIABLE output
  ERROR_VARIABLE error_output
)
if(result)
  message(FATAL_ERROR "Patch failed (exit code ${result}):\n${output}\n${error_output}")
endif()
